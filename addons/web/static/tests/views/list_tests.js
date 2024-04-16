flectra.define('web.list_tests',function(require){
"usestrict";

varAbstractFieldOwl=require('web.AbstractFieldOwl');
varAbstractStorageService=require('web.AbstractStorageService');
varBasicModel=require('web.BasicModel');
varcore=require('web.core');
constDomain=require('web.Domain')
varbasicFields=require('web.basic_fields');
varfieldRegistry=require('web.field_registry');
varfieldRegistryOwl=require('web.field_registry_owl');
varFormView=require('web.FormView');
varListRenderer=require('web.ListRenderer');
varListView=require('web.ListView');
varmixins=require('web.mixins');
varNotificationService=require('web.NotificationService');
varRamStorage=require('web.RamStorage');
vartestUtils=require('web.test_utils');
varwidgetRegistry=require('web.widget_registry');
varWidget=require('web.Widget');


var_t=core._t;
constcpHelpers=testUtils.controlPanel;
varcreateActionManager=testUtils.createActionManager;
varcreateView=testUtils.createView;

QUnit.module('Views',{
    beforeEach:function(){
        this.data={
            foo:{
                fields:{
                    foo:{string:"Foo",type:"char"},
                    bar:{string:"Bar",type:"boolean"},
                    date:{string:"SomeDate",type:"date"},
                    int_field:{string:"int_field",type:"integer",sortable:true,group_operator:"sum"},
                    text:{string:"textfield",type:"text"},
                    qux:{string:"myfloat",type:"float"},
                    m2o:{string:"M2Ofield",type:"many2one",relation:"bar"},
                    o2m:{string:"O2Mfield",type:"one2many",relation:"bar"},
                    m2m:{string:"M2Mfield",type:"many2many",relation:"bar"},
                    amount:{string:"Monetaryfield",type:"monetary"},
                    currency_id:{string:"Currency",type:"many2one",
                                  relation:"res_currency",default:1},
                    datetime:{string:"DatetimeField",type:'datetime'},
                    reference:{string:"ReferenceField",type:'reference',selection:[
                        ["bar","Bar"],["res_currency","Currency"],["event","Event"]]},
                },
                records:[
                    {
                        id:1,
                        bar:true,
                        foo:"yop",
                        int_field:10,
                        qux:0.4,
                        m2o:1,
                        m2m:[1,2],
                        amount:1200,
                        currency_id:2,
                        date:"2017-01-25",
                        datetime:"2016-12-1210:55:05",
                        reference:'bar,1',
                    },
                    {id:2,bar:true,foo:"blip",int_field:9,qux:13,
                     m2o:2,m2m:[1,2,3],amount:500,reference:'res_currency,1'},
                    {id:3,bar:true,foo:"gnap",int_field:17,qux:-3,
                     m2o:1,m2m:[],amount:300,reference:'res_currency,2'},
                    {id:4,bar:false,foo:"blip",int_field:-4,qux:9,
                     m2o:1,m2m:[1],amount:0},
                ]
            },
            bar:{
                fields:{},
                records:[
                    {id:1,display_name:"Value1"},
                    {id:2,display_name:"Value2"},
                    {id:3,display_name:"Value3"},
                ]
            },
            res_currency:{
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
            event:{
                fields:{
                    id:{string:"ID",type:"integer"},
                    name:{string:"name",type:"char"},
                },
                records:[
                    {id:"2-20170808020000",name:"virtual"},
                ]
            },
            "ir.translation":{
                fields:{
                    lang_code:{type:"char"},
                    src:{type:"char"},
                    value:{type:"char"},
                    res_id:{type:"integer"},
                    name:{type:"char"},
                    lang:{type:"char"},
                },
                records:[{
                    id:99,
                    res_id:1,
                    value:'',
                    lang_code:'en_US',
                    lang:'en_US',
                    name:'foo,foo'
                },{
                    id:100,
                    res_id:1,
                    value:'',
                    lang_code:'fr_BE',
                    lang:'fr_BE',
                    name:'foo,foo'
                }]
            },
        };
    }
},function(){

    QUnit.module('ListView');

    QUnit.test('simplereadonlylist',asyncfunction(assert){
        assert.expect(10);

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<tree><fieldname="foo"/><fieldname="int_field"/></tree>',
        });

        assert.doesNotHaveClass(list.$el,'o_cannot_create',
            "shouldnothaveclassName'o_cannot_create'");

        //3th(1forcheckbox,2forcolumns)
        assert.containsN(list,'th',3,"shouldhave3columns");

        assert.strictEqual(list.$('td:contains(gnap)').length,1,"shouldcontaingnap");
        assert.containsN(list,'tbodytr',4,"shouldhave4rows");
        assert.containsOnce(list,'th.o_column_sortable',"shouldhave1sortablecolumn");

        assert.strictEqual(list.$('theadth:nth(2)').css('text-align'),'right',
            "headercellsofintegerfieldsshouldberightaligned");
        assert.strictEqual(list.$('tbodytr:firsttd:nth(2)').css('text-align'),'right',
            "integercellsshouldberightaligned");

        assert.isVisible(list.$buttons.find('.o_list_button_add'));
        assert.isNotVisible(list.$buttons.find('.o_list_button_save'));
        assert.isNotVisible(list.$buttons.find('.o_list_button_discard'));
        list.destroy();
    });

    QUnit.test('on_attach_callbackisproperlycalled',asyncfunction(assert){
        assert.expect(3);

        testUtils.mock.patch(ListRenderer,{
            on_attach_callback(){
                assert.step('on_attach_callback');
                this._super(...arguments);
            },
        });

        constlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<tree><fieldname="display_name"/></tree>',
        });

        assert.verifySteps(['on_attach_callback']);
        awaitlist.reload();
        assert.verifySteps([]);

        testUtils.mock.unpatch(ListRenderer);
        list.destroy();
    });

    QUnit.test('listwithcreate="0"',asyncfunction(assert){
        assert.expect(2);

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<treecreate="0"><fieldname="foo"/></tree>',
        });

        assert.hasClass(list.$el,'o_cannot_create',
            "shouldhaveclassName'o_cannot_create'");
        assert.containsNone(list.$buttons,'.o_list_button_add',
            "shouldnothavethe'Create'button");

        list.destroy();
    });

    QUnit.test('listwithdelete="0"',asyncfunction(assert){
        assert.expect(3);

        constlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            viewOptions:{hasActionMenus:true},
            arch:'<treedelete="0"><fieldname="foo"/></tree>',
        });


        assert.containsNone(list.el,'div.o_control_panel.o_cp_action_menus');
        assert.ok(list.$('tbodytd.o_list_record_selector').length,'shouldhaveatleastonerecord');

        awaittestUtils.dom.click(list.$('tbodytd.o_list_record_selector:firstinput'));
        assert.containsNone(list.el,'div.o_control_panel.o_cp_action_menus.o_dropdown_menu');

        list.destroy();
    });

    QUnit.test('editablelistwithedit="0"',asyncfunction(assert){
        assert.expect(2);

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            viewOptions:{hasActionMenus:true},
            arch:'<treeeditable="top"edit="0"><fieldname="foo"/></tree>',
        });

        assert.ok(list.$('tbodytd.o_list_record_selector').length,'shouldhaveatleastonerecord');

        awaittestUtils.dom.click(list.$('trtd:not(.o_list_record_selector)').first());
        assert.containsNone(list,'tbodytr.o_selected_row',"shouldnothaveeditablerow");

        list.destroy();
    });

    QUnit.test('exportfeatureinlistforusersnotinbase.group_allow_export',asyncfunction(assert){
        assert.expect(5);

        constlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            viewOptions:{hasActionMenus:true},
            arch:'<tree><fieldname="foo"/></tree>',
            session:{
                asyncuser_has_group(group){
                    if(group==='base.group_allow_export'){
                        returnfalse;
                    }
                    returnthis._super(...arguments);
                },
            },
        });

        assert.containsNone(list.el,'div.o_control_panel.o_cp_action_menus');
        assert.ok(list.$('tbodytd.o_list_record_selector').length,'shouldhaveatleastonerecord');
        assert.containsNone(list.el,'div.o_control_panel.o_cp_buttons.o_list_export_xlsx');

        awaittestUtils.dom.click(list.$('tbodytd.o_list_record_selector:firstinput'));
        assert.containsOnce(list.el,'div.o_control_panel.o_cp_action_menus');
        awaitcpHelpers.toggleActionMenu(list);
        assert.deepEqual(cpHelpers.getMenuItemTexts(list),['Delete'],
            'actionmenushouldnotcontaintheExportbutton');

        list.destroy();
    });

    QUnit.test('listwithexportbutton',asyncfunction(assert){
        assert.expect(5);

        constlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            viewOptions:{hasActionMenus:true},
            arch:'<tree><fieldname="foo"/></tree>',
            session:{
                asyncuser_has_group(group){
                    if(group==='base.group_allow_export'){
                        returntrue;
                    }
                    returnthis._super(...arguments);
                },
            },
        });

        assert.containsNone(list.el,'div.o_control_panel.o_cp_action_menus');
        assert.ok(list.$('tbodytd.o_list_record_selector').length,'shouldhaveatleastonerecord');
        assert.containsOnce(list.el,'div.o_control_panel.o_cp_buttons.o_list_export_xlsx');

        awaittestUtils.dom.click(list.$('tbodytd.o_list_record_selector:firstinput'));
        assert.containsOnce(list.el,'div.o_control_panel.o_cp_action_menus');
        awaitcpHelpers.toggleActionMenu(list);
        assert.deepEqual(
            cpHelpers.getMenuItemTexts(list),
            ['Export','Delete'],
            'actionmenushouldhaveExportbutton'
        );

        list.destroy();
    });

    QUnit.test('exportbuttoninlistview',asyncfunction(assert){
        assert.expect(5);

        constlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<tree><fieldname="foo"/></tree>',
            session:{
                asyncuser_has_group(group){
                    if(group==='base.group_allow_export'){
                        returntrue;
                    }
                    returnthis._super(...arguments);
                },
            },
        });

        assert.containsN(list,'.o_data_row',4);
        assert.isVisible(list.$('.o_list_export_xlsx'));

        awaittestUtils.dom.click(list.$('tbodytd.o_list_record_selector:firstinput'));

        assert.isNotVisible(list.$('.o_list_export_xlsx'));
        assert.containsOnce(list.$('.o_cp_buttons'),'.o_list_selection_box');

        awaittestUtils.dom.click(list.$('tbodytd.o_list_record_selector:firstinput'));
        assert.isVisible(list.$('.o_list_export_xlsx'));

        list.destroy();
    });

    QUnit.test('exportbuttoninemptylistview',asyncfunction(assert){
        assert.expect(2);

        constlist=awaitcreateView({
            View:ListView,
            model:"foo",
            data:this.data,
            arch:'<tree><fieldname="foo"/></tree>',
            domain:[["id","<",0]],//suchthatnorecordmatchesthedomain
            session:{
                asyncuser_has_group(group){
                    if(group==='base.group_allow_export'){
                        returntrue;
                    }
                    returnthis._super(...arguments);
                },
            },
        });

        assert.isNotVisible(list.el.querySelector('.o_list_export_xlsx'));

        awaitlist.reload({domain:[['id','>',0]]});
        assert.isVisible(list.el.querySelector('.o_list_export_xlsx'));

        list.destroy();
    });

    QUnit.test('listviewwithadjacentbuttons',asyncfunction(assert){
        assert.expect(2);

        constlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:`
                <tree>
                    <buttonname="a"type="object"icon="fa-car"/>
                    <fieldname="foo"/>
                    <buttonname="x"type="object"icon="fa-star"/>
                    <buttonname="y"type="object"icon="fa-refresh"/>
                    <buttonname="z"type="object"icon="fa-exclamation"/>
                </tree>`,
        });

        assert.containsN(list,'th',4,
            "adjacentbuttonsinthearchmustbegroupedinasinglecolumn");
        assert.containsN(list.$('.o_data_row:first'),'td.o_list_button',2);

        list.destroy();
    });

    QUnit.test('listviewwithadjacentbuttonsandinvisiblefield',asyncfunction(assert){
        assert.expect(2);

        constlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:`
                <tree>
                    <buttonname="a"type="object"icon="fa-car"/>
                    <fieldname="foo"invisible="1"/>
                    <buttonname="x"type="object"icon="fa-star"/>
                    <buttonname="y"type="object"icon="fa-refresh"/>
                    <buttonname="z"type="object"icon="fa-exclamation"/>
                </tree>`,
        });

        assert.containsN(list,'th',3,
            "adjacentbuttonsinthearchmustbegroupedinasinglecolumn");
        assert.containsN(list.$('.o_data_row:first'),'td.o_list_button',2);

        list.destroy();
    });

    QUnit.test('listviewwithadjacentbuttonsandinvisiblefield(modifier)',asyncfunction(assert){
        assert.expect(2);

        constlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:`
                <tree>
                    <buttonname="a"type="object"icon="fa-car"/>
                    <fieldname="foo"attrs="{'invisible':[['foo','=','blip']]}"/>
                    <buttonname="x"type="object"icon="fa-star"/>
                    <buttonname="y"type="object"icon="fa-refresh"/>
                    <buttonname="z"type="object"icon="fa-exclamation"/>
                </tree>`,
        });

        assert.containsN(list,'th',4,
            "adjacentbuttonsinthearchmustbegroupedinasinglecolumn");
        assert.containsN(list.$('.o_data_row:first'),'td.o_list_button',2);

        list.destroy();
    });

    QUnit.test('listviewwithadjacentbuttonsandoptionalfield',asyncfunction(assert){
        assert.expect(2);

        constlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:`
                <tree>
                    <buttonname="a"type="object"icon="fa-car"/>
                    <fieldname="foo"optional="hide"/>
                    <buttonname="x"type="object"icon="fa-star"/>
                    <buttonname="y"type="object"icon="fa-refresh"/>
                    <buttonname="z"type="object"icon="fa-exclamation"/>
                </tree>`,
        });

        assert.containsN(list,'th',3,
            "adjacentbuttonsinthearchmustbegroupedinasinglecolumn");
        assert.containsN(list.$('.o_data_row:first'),'td.o_list_button',2);

        list.destroy();
    });

    QUnit.test('listviewwithadjacentbuttonswithinvisiblemodifier',asyncfunction(assert){
        assert.expect(6);

        constlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:`
                <tree>
                    <fieldname="foo"/>
                    <buttonname="x"type="object"icon="fa-star"attrs="{'invisible':[['foo','=','blip']]}"/>
                    <buttonname="y"type="object"icon="fa-refresh"attrs="{'invisible':[['foo','=','yop']]}"/>
                    <buttonname="z"type="object"icon="fa-exclamation"attrs="{'invisible':[['foo','=','gnap']]}"/>
                </tree>`,
        });

        assert.containsN(list,'th',3,
            "adjacentbuttonsinthearchmustbegroupedinasinglecolumn");
        assert.containsOnce(list.$('.o_data_row:first'),'td.o_list_button');
        assert.strictEqual(list.$('.o_field_cell').text(),'yopblipgnapblip');
        assert.containsN(list,'tdbuttoni.fa-star:visible',2);
        assert.containsN(list,'tdbuttoni.fa-refresh:visible',3);
        assert.containsN(list,'tdbuttoni.fa-exclamation:visible',3);

        list.destroy();
    });

    QUnit.test('listviewwithiconbuttons',asyncfunction(assert){
        assert.expect(5);

        this.data.foo.records.splice(1);

        constlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:`
                <tree>
                    <buttonname="x"type="object"icon="fa-asterisk"/>
                    <buttonname="x"type="object"icon="fa-star"class="o_yeah"/>
                    <buttonname="x"type="object"icon="fa-refresh"string="Refresh"class="o_yeah"/>
                    <buttonname="x"type="object"icon="fa-exclamation"string="Danger"class="o_yeahbtn-danger"/>
                </tree>`,
        });

        assert.containsOnce(list,'button.btn.btn-linki.fa.fa-asterisk');
        assert.containsOnce(list,'button.btn.btn-link.o_yeahi.fa.fa-star');
        assert.containsOnce(list,'button.btn.btn-link.o_yeah:contains("Refresh")i.fa.fa-refresh');
        assert.containsOnce(list,'button.btn.btn-danger.o_yeah:contains("Danger")i.fa.fa-exclamation');
        assert.containsNone(list,'button.btn.btn-link.btn-danger');

        list.destroy();
    });

    QUnit.test('listview:actionbuttonincontrolPanelbasicrendering',asyncfunction(assert){
        assert.expect(11);

        constlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:`
                <tree>
                    <header>
                         <buttonname="x"type="object"class="plaf"string="plaf"/>
                         <buttonname="y"type="object"class="plouf"string="plouf"invisible="notcontext.get('bim')"/>
                    </header>
                    <fieldname="foo"/>
                </tree>`,
        });
        letcpButtons=cpHelpers.getButtons(list);
        assert.containsNone(cpButtons[0],'button[name="x"]');
        assert.containsNone(cpButtons[0],'.o_list_selection_box');
        assert.containsNone(cpButtons[0],'button[name="y"]');

        awaittestUtils.dom.click(
            list.el.querySelector('.o_data_row.o_list_record_selectorinput[type="checkbox"]')
        );
        cpButtons=cpHelpers.getButtons(list);
        assert.containsOnce(cpButtons[0],'button[name="x"]');
        assert.hasClass(cpButtons[0].querySelector('button[name="x"]'),'btnbtn-secondary');
        assert.containsOnce(cpButtons[0],'.o_list_selection_box');
        assert.strictEqual(
            cpButtons[0].querySelector('button[name="x"]').previousElementSibling,
            cpButtons[0].querySelector('.o_list_selection_box')
        );
        assert.containsNone(cpButtons[0],'button[name="y"]');

        awaittestUtils.dom.click(
            list.el.querySelector('.o_data_row.o_list_record_selectorinput[type="checkbox"]')
        );
        cpButtons=cpHelpers.getButtons(list);
        assert.containsNone(cpButtons[0],'button[name="x"]');
        assert.containsNone(cpButtons[0],'.o_list_selection_box');
        assert.containsNone(cpButtons[0],'button[name="y"]');

        list.destroy();
    });

    QUnit.test('listview:actionbuttonexecutesactiononclick:buttonsaredisabledandre-enabled',asyncfunction(assert){
        assert.expect(3);

        constexecuteActionDef=testUtils.makeTestPromise();
        constlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:`
                <tree>
                    <header>
                         <buttonname="x"type="object"class="plaf"string="plaf"/>
                    </header>
                    <fieldname="foo"/>
                </tree>`,
            intercepts:{
                asyncexecute_action(ev){
                    const{on_success}=ev.data;
                    awaitexecuteActionDef;
                    on_success();
                }
            }
        });
        awaittestUtils.dom.click(
            list.el.querySelector('.o_data_row.o_list_record_selectorinput[type="checkbox"]')
        );
        constcpButtons=cpHelpers.getButtons(list);
        assert.ok(
            Array.from(cpButtons[0].querySelectorAll('button')).every(btn=>!btn.disabled)
        );

        awaittestUtils.dom.click(cpButtons[0].querySelector('button[name="x"]'));
        assert.ok(
            Array.from(cpButtons[0].querySelectorAll('button')).every(btn=>btn.disabled)
        );

        executeActionDef.resolve();
        awaittestUtils.nextTick();
        assert.ok(
            Array.from(cpButtons[0].querySelectorAll('button')).every(btn=>!btn.disabled)
        );

        list.destroy();
    });

    QUnit.test('listview:actionbuttonexecutesactiononclick:correctparameters',asyncfunction(assert){
        assert.expect(4);

        constlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:`
                <tree>
                    <header>
                         <buttonname="x"type="object"class="plaf"string="plaf"context="{'plouf':'plif'}"/>
                    </header>
                    <fieldname="foo"/>
                </tree>`,
            intercepts:{
                asyncexecute_action(ev){
                    const{
                        action_data:{
                            context,name,type
                        },
                        env,
                    }=ev.data;
                    //Action'sownproperties
                    assert.strictEqual(name,"x");
                    assert.strictEqual(type,"object");

                    //Theaction'sexecutioncontext
                    assert.deepEqual(context,{
                        active_domain:[],
                        active_id:1,
                        active_ids:[1],
                        active_model:'foo',
                        plouf:'plif',
                    });
                    //Thecurrentenvironment(notowl's,butthecurrentaction's)
                    assert.deepEqual(env,{
                        context:{},
                        model:'foo',
                        resIDs:[1],
                    });
                }
            }
        });
        awaittestUtils.dom.click(
            list.el.querySelector('.o_data_row.o_list_record_selectorinput[type="checkbox"]')
        );
        constcpButtons=cpHelpers.getButtons(list);
        awaittestUtils.dom.click(cpButtons[0].querySelector('button[name="x"]'));
        list.destroy();
    });

    QUnit.test('listview:actionbuttonexecutesactiononclickwithdomainselected:correctparameters',asyncfunction(assert){
        assert.expect(10);

        constlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:`
                <treelimit="1">
                    <header>
                         <buttonname="x"type="object"class="plaf"string="plaf"/>
                    </header>
                    <fieldname="foo"/>
                </tree>`,
            intercepts:{
                asyncexecute_action(ev){
                    assert.step('execute_action');
                    const{
                        action_data:{
                            context,name,type
                        },
                        env,
                    }=ev.data;
                    //Action'sownproperties
                    assert.strictEqual(name,"x");
                    assert.strictEqual(type,"object");

                    //Theaction'sexecutioncontext
                    assert.deepEqual(context,{
                        active_domain:[],
                        active_id:1,
                        active_ids:[1,2,3,4],
                        active_model:'foo',
                    });
                    //Thecurrentenvironment(notowl's,butthecurrentaction's)
                    assert.deepEqual(env,{
                        context:{},
                        model:'foo',
                        resIDs:[1,2,3,4],
                    });
                }
            },
            mockRPC(route,args){
                if(args.method==='search'){
                    assert.step('search');
                    assert.strictEqual(args.model,'foo');
                    assert.deepEqual(args.args,[[]]);//emptydomainsincenodomaininsearchView
                }
                returnthis._super.call(this,...arguments);
            }
        });
        awaittestUtils.dom.click(
            list.el.querySelector('.o_data_row.o_list_record_selectorinput[type="checkbox"]')
        );
        constcpButtons=cpHelpers.getButtons(list);

        awaittestUtils.dom.click(cpButtons[0].querySelector('.o_list_select_domain'));
        assert.verifySteps([]);

        awaittestUtils.dom.click(cpButtons[0].querySelector('button[name="x"]'));
        assert.verifySteps([
            'search',
            'execute_action',
        ]);

        list.destroy();
    });

    QUnit.test('columnnames(noLabel,label,stringanddefault)',asyncfunction(assert){
        assert.expect(4);

        constFieldChar=fieldRegistry.get('char');
        fieldRegistry.add('nolabel_char',FieldChar.extend({
            noLabel:true,
        }));
        fieldRegistry.add('label_char',FieldChar.extend({
            label:"Somestaticlabel",
        }));

        constlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:`
                <tree>
                    <fieldname="display_name"widget="nolabel_char"/>
                    <fieldname="foo"widget="label_char"/>
                    <fieldname="int_field"string="Mycustomlabel"/>
                    <fieldname="text"/>
                </tree>`,
        });

        assert.strictEqual(list.$('theadth[data-name=display_name]').text(),'');
        assert.strictEqual(list.$('theadth[data-name=foo]').text(),'Somestaticlabel');
        assert.strictEqual(list.$('theadth[data-name=int_field]').text(),'Mycustomlabel');
        assert.strictEqual(list.$('theadth[data-name=text]').text(),'textfield');

        list.destroy();
    });

    QUnit.test('simpleeditablerendering',asyncfunction(assert){
        assert.expect(15);

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<treeeditable="bottom"><fieldname="foo"/><fieldname="bar"/></tree>',
        });

        assert.containsN(list,'th',3,"shouldhave2th");
        assert.containsN(list,'th',3,"shouldhave3th");
        assert.containsN(list,'.o_list_record_selectorinput:enabled',5);
        assert.containsOnce(list,'td:contains(yop)',"shouldcontainyop");

        assert.isVisible(list.$buttons.find('.o_list_button_add'),
            "shouldhaveavisibleCreatebutton");
        assert.isNotVisible(list.$buttons.find('.o_list_button_save'),
            "shouldnothaveavisiblesavebutton");
        assert.isNotVisible(list.$buttons.find('.o_list_button_discard'),
            "shouldnothaveavisiblediscardbutton");

        awaittestUtils.dom.click(list.$('td:not(.o_list_record_selector)').first());

        assert.isNotVisible(list.$buttons.find('.o_list_button_add'),
            "shouldnothaveavisibleCreatebutton");
        assert.isVisible(list.$buttons.find('.o_list_button_save'),
            "shouldhaveavisiblesavebutton");
        assert.isVisible(list.$buttons.find('.o_list_button_discard'),
            "shouldhaveavisiblediscardbutton");
        assert.containsNone(list,'.o_list_record_selectorinput:enabled');

        awaittestUtils.dom.click(list.$buttons.find('.o_list_button_save'));

        assert.isVisible(list.$buttons.find('.o_list_button_add'),
            "shouldhaveavisibleCreatebutton");
        assert.isNotVisible(list.$buttons.find('.o_list_button_save'),
            "shouldnothaveavisiblesavebutton");
        assert.isNotVisible(list.$buttons.find('.o_list_button_discard'),
            "shouldnothaveavisiblediscardbutton");
        assert.containsN(list,'.o_list_record_selectorinput:enabled',5);

        list.destroy();
    });

    QUnit.test('editablerenderingwithhandleandnodata',asyncfunction(assert){
        assert.expect(6);

        this.data.foo.records=[];
        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<treeeditable="bottom">'+
                    '<fieldname="int_field"widget="handle"/>'+
                    '<fieldname="currency_id"/>'+
                    '<fieldname="m2o"/>'+
                '</tree>',
        });
        assert.containsN(list,'theadth',4,"thereshouldbe4th");
        assert.hasClass(list.$('theadth:eq(0)'),'o_list_record_selector');
        assert.hasClass(list.$('theadth:eq(1)'),'o_handle_cell');
        assert.strictEqual(list.$('theadth:eq(1)').text(),'',
            "thehandlefieldshouldn'thaveaheaderdescription");
        assert.strictEqual(list.$('theadth:eq(2)').attr('style'),"width:50%;");
        assert.strictEqual(list.$('theadth:eq(3)').attr('style'),"width:50%;");
        list.destroy();
    });

    QUnit.test('invisiblecolumnsarenotdisplayed',asyncfunction(assert){
        assert.expect(1);

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<tree>'+
                    '<fieldname="foo"/>'+
                    '<fieldname="bar"invisible="1"/>'+
                '</tree>',
        });

        //1thforcheckbox,1for1visiblecolumn
        assert.containsN(list,'th',2,"shouldhave2th");
        list.destroy();
    });

    QUnit.test('booleanfieldhasnotitle',asyncfunction(assert){
        assert.expect(1);

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<tree><fieldname="bar"/></tree>',
        });
        assert.equal(list.$('tbodytr:firsttd:eq(1)').attr('title'),"");
        list.destroy();
    });

    QUnit.test('fieldwithnolabelhasnotitle',asyncfunction(assert){
        assert.expect(1);

        constlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<tree><fieldname="foo"nolabel="1"/></tree>',
        });
        assert.strictEqual(list.$('theadtr:firstth:eq(1)').text(),"");
        list.destroy();
    });

    QUnit.test('fieldtitlesarenotescaped',asyncfunction(assert){
        assert.expect(2);

        this.data.foo.records[0].foo='<div>Hello</div>';

        constlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<tree><fieldname="foo"/></tree>',
        });

        assert.strictEqual(list.$('tbodytr:first.o_data_cell').text(),"<div>Hello</div>");
        assert.strictEqual(list.$('tbodytr:first.o_data_cell').attr('title'),"<div>Hello</div>");

        list.destroy();
    });

    QUnit.test('record-dependinginvisiblelinesarecorrectlyaligned',asyncfunction(assert){
        assert.expect(4);

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<tree>'+
                    '<fieldname="foo"/>'+
                    '<fieldname="bar"attrs="{\'invisible\':[(\'id\',\'=\',1)]}"/>'+
                    '<fieldname="int_field"/>'+
                '</tree>',
        });

        assert.containsN(list,'tbodytr:firsttd',4,
            "thereshouldbe4cellsinthefirstrow");
        assert.containsOnce(list,'tbodytd.o_invisible_modifier',
            "thereshouldbe1invisiblebarcell");
        assert.hasClass(list.$('tbodytr:firsttd:eq(2)'),'o_invisible_modifier',
            "the3rdcellshouldbeinvisible");
        assert.containsN(list,'tbodytr:eq(0)td:visible',list.$('tbodytr:eq(1)td:visible').length,
            "thereshouldbethesamenumberofvisiblecellsindifferentrows");
        list.destroy();
    });

    QUnit.test('donotperformextraRPCtoreadinvisiblemany2onefields',asyncfunction(assert){
        assert.expect(3);

        this.data.foo.fields.m2o.default=2;

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<treeeditable="top">'+
                    '<fieldname="foo"/>'+
                    '<fieldname="m2o"invisible="1"/>'+
                '</tree>',
            mockRPC:function(route){
                assert.step(_.last(route.split('/')));
                returnthis._super.apply(this,arguments);
            },
        });

        awaittestUtils.dom.click(list.$buttons.find('.o_list_button_add'));
        assert.verifySteps(['search_read','onchange'],"nonamegetshouldbedone");

        list.destroy();
    });

    QUnit.test('editablelistdatetimepickerdestroywidget(edition)',asyncfunction(assert){
        assert.expect(7);
        vareventPromise=testUtils.makeTestPromise();

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<treeeditable="top">'+
                    '<fieldname="date"/>'+
                '</tree>',
        });
        list.$el.on({
            'show.datetimepicker':asyncfunction(){
                assert.containsOnce(list,'.o_selected_row');
                assert.containsOnce($('body'),'.bootstrap-datetimepicker-widget');

                awaittestUtils.fields.triggerKeydown(list.$('.o_datepicker_input'),'escape');

                assert.containsOnce(list,'.o_selected_row');
                assert.containsNone($('body'),'.bootstrap-datetimepicker-widget');

                awaittestUtils.fields.triggerKeydown($(document.activeElement),'escape');

                assert.containsNone(list,'.o_selected_row');

                eventPromise.resolve();
            }
        });

        assert.containsN(list,'.o_data_row',4);
        assert.containsNone(list,'.o_selected_row');

        awaittestUtils.dom.click(list.$('.o_data_cell:first'));
        awaittestUtils.dom.openDatepicker(list.$('.o_datepicker'));

        awaiteventPromise;
        list.destroy();
    });

    QUnit.test('editablelistdatetimepickerdestroywidget(newline)',asyncfunction(assert){
        assert.expect(10);
        vareventPromise=testUtils.makeTestPromise();

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<treeeditable="top">'+
                    '<fieldname="date"/>'+
                '</tree>',
        });
        list.$el.on({
            'show.datetimepicker':asyncfunction(){
                assert.containsOnce($('body'),'.bootstrap-datetimepicker-widget');
                assert.containsN(list,'.o_data_row',5);
                assert.containsOnce(list,'.o_selected_row');

                awaittestUtils.fields.triggerKeydown(list.$('.o_datepicker_input'),'escape');

                assert.containsNone($('body'),'.bootstrap-datetimepicker-widget');
                assert.containsN(list,'.o_data_row',5);
                assert.containsOnce(list,'.o_selected_row');

                awaittestUtils.fields.triggerKeydown($(document.activeElement),'escape');

                assert.containsN(list,'.o_data_row',4);
                assert.containsNone(list,'.o_selected_row');

                eventPromise.resolve();
            }
        });
        assert.equal(list.$('.o_data_row').length,4,
            'Thereshouldbe4rows');

        assert.equal(list.$('.o_selected_row').length,0,
            'Norowshouldbeineditmode');

        awaittestUtils.dom.click(list.$buttons.find('.o_list_button_add'));
        awaittestUtils.dom.openDatepicker(list.$('.o_datepicker'));

        awaiteventPromise;
        list.destroy();
    });

    QUnit.test('atleast4rowsarerendered,eveniflessdata',asyncfunction(assert){
        assert.expect(1);

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<tree><fieldname="bar"/></tree>',
            domain:[['bar','=',true]],
        });

        assert.containsN(list,'tbodytr',4,"shouldhave4rows");
        list.destroy();
    });

    QUnit.test('discardanewrecordineditable="top"listwithlessthan4records',asyncfunction(assert){
        assert.expect(7);

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<treeeditable="top"><fieldname="bar"/></tree>',
            domain:[['bar','=',true]],
        });

        assert.containsN(list,'.o_data_row',3);
        assert.containsN(list,'tbodytr',4);

        awaittestUtils.dom.click(list.$('.o_list_button_add'));

        assert.containsN(list,'.o_data_row',4);
        assert.hasClass(list.$('tbodytr:first'),'o_selected_row');

        awaittestUtils.dom.click(list.$('.o_list_button_discard'));

        assert.containsN(list,'.o_data_row',3);
        assert.containsN(list,'tbodytr',4);
        assert.hasClass(list.$('tbodytr:first'),'o_data_row');

        list.destroy();
    });

    QUnit.test('basicgroupedlistrendering',asyncfunction(assert){
        assert.expect(4);

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<tree><fieldname="foo"/><fieldname="bar"/></tree>',
            groupBy:['bar'],
        });

        assert.strictEqual(list.$('th:contains(Foo)').length,1,"shouldcontainFoo");
        assert.strictEqual(list.$('th:contains(Bar)').length,1,"shouldcontainBar");
        assert.containsN(list,'tr.o_group_header',2,"shouldhave2.o_group_header");
        assert.containsN(list,'th.o_group_name',2,"shouldhave2.o_group_name");
        list.destroy();
    });

    QUnit.test('basicgroupedlistrenderingwithwidget="handle"col',asyncfunction(assert){
        assert.expect(5);

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<tree>'+
                    '<fieldname="int_field"widget="handle"/>'+
                    '<fieldname="foo"/>'+
                    '<fieldname="bar"/>'+
                '</tree>',
            groupBy:['bar'],
        });

        assert.strictEqual(list.$('th:contains(Foo)').length,1,"shouldcontainFoo");
        assert.strictEqual(list.$('th:contains(Bar)').length,1,"shouldcontainBar");
        assert.containsN(list,'tr.o_group_header',2,"shouldhave2.o_group_header");
        assert.containsN(list,'th.o_group_name',2,"shouldhave2.o_group_name");
        assert.containsNone(list,'th:contains(int_field)',"Shouldnothaveint_fieldingroupedlist");
        list.destroy();
    });

    QUnit.test('basicgroupedlistrendering1colwithoutselector',asyncfunction(assert){
        assert.expect(2);

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<tree><fieldname="foo"/></tree>',
            groupBy:['bar'],
            hasSelectors:false,
        });

        assert.strictEqual(list.$('.o_group_header:first').children().length,1,
            "groupheadershouldhaveexactly1column");
        assert.strictEqual(list.$('.o_group_header:firstth').attr('colspan'),"1",
            "theheadershouldspanthewholetable");
        list.destroy();
    });

    QUnit.test('basicgroupedlistrendering1colwithselector',asyncfunction(assert){
        assert.expect(2);

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<tree><fieldname="foo"/></tree>',
            groupBy:['bar'],
            hasSelectors:true,
        });

        assert.strictEqual(list.$('.o_group_header:first').children().length,1,
            "groupheadershouldhaveexactly1column");
        assert.strictEqual(list.$('.o_group_header:firstth').attr('colspan'),"2",
            "theheadershouldspanthewholetable");
        list.destroy();
    });

    QUnit.test('basicgroupedlistrendering2colswithoutselector',asyncfunction(assert){
        assert.expect(2);

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<tree><fieldname="foo"/><fieldname="bar"/></tree>',
            groupBy:['bar'],
            hasSelectors:false,
        });

        assert.strictEqual(list.$('.o_group_header:first').children().length,2,
            "groupheadershouldhaveexactly2column");
        assert.strictEqual(list.$('.o_group_header:firstth').attr('colspan'),"1",
            "theheadershouldnotspanthewholetable");
        list.destroy();
    });

    QUnit.test('basicgroupedlistrendering3colswithoutselector',asyncfunction(assert){
        assert.expect(2);

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<tree><fieldname="foo"/><fieldname="bar"/><fieldname="text"/></tree>',
            groupBy:['bar'],
            hasSelectors:false,
        });

        assert.strictEqual(list.$('.o_group_header:first').children().length,2,
            "groupheadershouldhaveexactly2columns");
        assert.strictEqual(list.$('.o_group_header:firstth').attr('colspan'),"2",
            "thefirstheadershould spantwocolumns");
        list.destroy();
    });

    QUnit.test('basicgroupedlistrendering2colwithselector',asyncfunction(assert){
        assert.expect(2);

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<tree><fieldname="foo"/><fieldname="bar"/></tree>',
            groupBy:['bar'],
            hasSelectors:true,
        });

        assert.strictEqual(list.$('.o_group_header:first').children().length,2,
            "groupheadershouldhaveexactly2columns");
        assert.strictEqual(list.$('.o_group_header:firstth').attr('colspan'),"2",
            "theheadershouldnotspanthewholetable");
        list.destroy();
    });

    QUnit.test('basicgroupedlistrendering3colswithselector',asyncfunction(assert){
        assert.expect(2);

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<tree><fieldname="foo"/><fieldname="bar"/><fieldname="text"/></tree>',
            groupBy:['bar'],
            hasSelectors:true,
        });

        assert.strictEqual(list.$('.o_group_header:first').children().length,2,
            "groupheadershouldhaveexactly2columns");
        assert.strictEqual(list.$('.o_group_header:firstth').attr('colspan'),"3",
            "theheadershouldnotspanthewholetable");
        list.destroy();
    });

    QUnit.test('basicgroupedlistrendering7colswithaggregatesandselector',asyncfunction(assert){
        assert.expect(4);

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<tree>'+
                    '<fieldname="datetime"/>'+
                    '<fieldname="foo"/>'+
                    '<fieldname="int_field"sum="Sum1"/>'+
                    '<fieldname="bar"/>'+
                    '<fieldname="qux"sum="Sum2"/>'+
                    '<fieldname="date"/>'+
                    '<fieldname="text"/>'+
                '</tree>',
            groupBy:['bar'],
        });

        assert.strictEqual(list.$('.o_group_header:first').children().length,5,
            "groupheadershouldhaveexactly5columns(onebeforefirstaggregate,oneafterlastaggregate,andallinbetween");
        assert.strictEqual(list.$('.o_group_header:firstth').attr('colspan'),"3",
            "headernameshouldspanonthetwofirstfields+selector(colspan3)");
        assert.containsN(list,'.o_group_header:firsttd',3,
            "thereshouldbe3tds(aggregates+fieldsinbetween)");
        assert.strictEqual(list.$('.o_group_header:firstth:last').attr('colspan'),"2",
            "headerlastcellshouldspanonthetwolastfields(togivespaceforthepager)(colspan2)");
        list.destroy();
    });

    QUnit.test('orderedlist,sortattributeincontext',asyncfunction(assert){
        assert.expect(1);
        //Equivalenttosavingacustomfilter

        this.data.foo.fields.foo.sortable=true;
        this.data.foo.fields.date.sortable=true;

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<tree>'+
                    '<fieldname="foo"/>'+
                    '<fieldname="date"/>'+
                '</tree>',
        });

        //DescendingorderonFoo
        awaittestUtils.dom.click(list.$('th.o_column_sortable:contains("Foo")'));
        awaittestUtils.dom.click(list.$('th.o_column_sortable:contains("Foo")'));

        //AscendingorderonDate
        awaittestUtils.dom.click(list.$('th.o_column_sortable:contains("Date")'));

        varlistContext=list.getOwnedQueryParams();
        assert.deepEqual(listContext,
            {
                orderedBy:[{
                    name:'date',
                    asc:true,
                },{
                    name:'foo',
                    asc:false,
                }]
            },'thelistshouldhavetherightorderedByincontext');
        list.destroy();
    });

    QUnit.test('Loadingafilterwithasortattribute',asyncfunction(assert){
        assert.expect(2);

        this.data.foo.fields.foo.sortable=true;
        this.data.foo.fields.date.sortable=true;

        varsearchReads=0;
        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<tree>'+
                    '<fieldname="foo"/>'+
                    '<fieldname="date"/>'+
                '</tree>',
            mockRPC:function(route,args){
                if(route==='/web/dataset/search_read'){
                    if(searchReads===0){
                        assert.strictEqual(args.sort,'dateASC,fooDESC',
                            'Thesortattributeofthefiltershouldbeusedbytheinitialsearch_read');
                    }elseif(searchReads===1){
                        assert.strictEqual(args.sort,'dateDESC,fooASC',
                            'Thesortattributeofthefiltershouldbeusedbythenextsearch_read');
                    }
                    searchReads+=1;
                }
                returnthis._super.apply(this,arguments);
            },
            favoriteFilters:[
                {
                    context:"{}",
                    domain:"[]",
                    id:7,
                    is_default:true,
                    name:"Myfavorite",
                    sort:"[\"dateasc\",\"foodesc\"]",
                    user_id:[2,"MitchellAdmin"],
                },{
                    context:"{}",
                    domain:"[]",
                    id:8,
                    is_default:false,
                    name:"Mysecondfavorite",
                    sort:"[\"datedesc\",\"fooasc\"]",
                    user_id:[2,"MitchellAdmin"],
                }
            ]
        });


        awaitcpHelpers.toggleFavoriteMenu(list);
        awaitcpHelpers.toggleMenuItem(list,"Mysecondfavorite");

        list.destroy();
    });

    QUnit.test('many2onefieldrendering',asyncfunction(assert){
        assert.expect(1);

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<tree><fieldname="m2o"/></tree>',
        });

        assert.ok(list.$('td:contains(Value1)').length,
            "shouldhavethedisplay_nameofthemany2one");
        list.destroy();
    });

    QUnit.test('groupedlistview,with1opengroup',asyncfunction(assert){
        assert.expect(6);

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<tree><fieldname="foo"/><fieldname="int_field"/></tree>',
            groupBy:['foo'],
        });

        awaittestUtils.dom.click(list.$('th.o_group_name:nth(1)'));
        awaittestUtils.nextTick();
        assert.containsN(list,'tbody:eq(1)tr',2,"opengroupshouldcontain2records");
        assert.containsN(list,'tbody',3,"shouldcontain3tbody");
        assert.containsOnce(list,'td:contains(9)',"shouldcontain9");
        assert.containsOnce(list,'td:contains(-4)',"shouldcontain-4");
        assert.containsOnce(list,'td:contains(10)',"shouldcontain10");
        assert.containsOnce(list,'tr.o_group_headertd:contains(10)',"but10shouldbeinaheader");
        list.destroy();
    });

    QUnit.test('openingrecordswhenclickingonrecord',asyncfunction(assert){
        assert.expect(3);

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<tree><fieldname="foo"/></tree>',
        });

        testUtils.mock.intercept(list,"open_record",function(){
            assert.ok("listviewshouldtrigger'open_record'event");
        });

        awaittestUtils.dom.click(list.$('trtd:not(.o_list_record_selector)').first());
        list.update({groupBy:['foo']});
        awaittestUtils.nextTick();

        assert.containsN(list,'tr.o_group_header',3,"listshouldbegrouped");
        awaittestUtils.dom.click(list.$('th.o_group_name').first());

        testUtils.dom.click(list.$('tr:not(.o_group_header)td:not(.o_list_record_selector)').first());
        list.destroy();
    });

    QUnit.test('editablelistview:readonlyfieldscannotbeedited',asyncfunction(assert){
        assert.expect(4);

        this.data.foo.fields.foo.readonly=true;

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<treeeditable="bottom">'+
                    '<fieldname="foo"/>'+
                    '<fieldname="bar"/>'+
                    '<fieldname="int_field"readonly="1"/>'+
                '</tree>',
        });
        var$td=list.$('td:not(.o_list_record_selector)').first();
        var$second_td=list.$('td:not(.o_list_record_selector)').eq(1);
        var$third_td=list.$('td:not(.o_list_record_selector)').eq(2);
        awaittestUtils.dom.click($td);
        assert.hasClass($td.parent(),'o_selected_row',
            "rowshouldbeineditmode");
        assert.hasClass($td,'o_readonly_modifier',
            "foocellshouldbereadonlyineditmode");
        assert.doesNotHaveClass($second_td,'o_readonly_modifier',
            "barcellshouldbeeditable");
        assert.hasClass($third_td,'o_readonly_modifier',
            "int_fieldcellshouldbereadonlyineditmode");
        list.destroy();
    });

    QUnit.test('editablelistview:linewithnoactiveelement',asyncfunction(assert){
        assert.expect(3);

        this.data.bar={
            fields:{
                titi:{string:"Char",type:"char"},
                grosminet:{string:"Bool",type:"boolean"},
            },
            records:[
                {id:1,titi:'cui',grosminet:true},
                {id:2,titi:'cuicui',grosminet:false},
            ],
        };
        this.data.foo.records[0].o2m=[1,2];

        varform=awaitcreateView({
            View:FormView,
            model:'foo',
            data:this.data,
            res_id:1,
            viewOptions:{mode:'edit'},
            arch:'<form>'+
                    '<fieldname="o2m">'+
                        '<treeeditable="top">'+
                            '<fieldname="titi"readonly="1"/>'+
                            '<fieldname="grosminet"widget="boolean_toggle"/>'+
                        '</tree>'+
                    '</field>'+
                '</form>',
            mockRPC:function(route,args){
                if(args.method==='write'){
                    assert.deepEqual(args.args[1],{
                        o2m:[[1,1,{grosminet:false}],[4,2,false]],
                    });
                }
                returnthis._super.apply(this,arguments);
            },
        });

        var$td=form.$('.o_data_cell').first();
        var$td2=form.$('.o_data_cell').eq(1);
        assert.hasClass($td,'o_readonly_modifier');
        assert.hasClass($td2,'o_boolean_toggle_cell');
        awaittestUtils.dom.click($td);
        awaittestUtils.dom.click($td2.find('.o_boolean_toggleinput'));
        awaittestUtils.nextTick();

        awaittestUtils.form.clickSave(form);
        awaittestUtils.nextTick();
        form.destroy();
    });

    QUnit.test('editablelistview:clickonlastelementaftercreationemptynewline',asyncfunction(assert){
        assert.expect(1);

        this.data.bar={
            fields:{
                titi:{string:"Char",type:"char",required:true},
                int_field:{string:"int_field",type:"integer",sortable:true,required:true}
            },
            records:[
                {id:1,titi:'cui',int_field:2},
                {id:2,titi:'cuicui',int_field:4},
            ],
        };
        this.data.foo.records[0].o2m=[1,2];

        varform=awaitcreateView({
            View:FormView,
            model:'foo',
            data:this.data,
            res_id:1,
            viewOptions:{mode:'edit'},
            arch:'<form>'+
                    '<fieldname="o2m">'+
                        '<treeeditable="top">'+
                            '<fieldname="int_field"widget="handle"/>'+
                            '<fieldname="titi"/>'+
                        '</tree>'+
                    '</field>'+
                '</form>',
        });
        awaittestUtils.dom.click(form.$('.o_field_x2many_list_row_add>a'));
        awaittestUtils.dom.click(form.$('.o_data_row:last()>td.o_list_char'));
        //Thistestensurethattheyaren'ttracebackwhenclickingonthelastrow.
        assert.containsN(form,'.o_data_row',2,"listshouldhaveexactly2rows");
        form.destroy();
    });

    QUnit.test('editfieldineditablefieldwithouteditingtherow',asyncfunction(assert){
        //somewidgetsareeditableinreadonly(e.g.priority,boolean_toggle...)andthey
        //thusdon'trequiretherowtobeswitchedineditiontobeedited
        assert.expect(13);

        constlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:`
                <treeeditable="top">
                    <fieldname="foo"/>
                    <fieldname="bar"widget="boolean_toggle"/>
                </tree>`,
            mockRPC(route,args){
                if(args.method==='write'){
                    assert.step('write:'+args.args[1].bar);
                }
                returnthis._super(...arguments);
            },
        });

        //togglethebooleanvalueofthefirstrowwithouteditingtherow
        assert.ok(list.$('.o_data_row:first.o_boolean_toggleinput')[0].checked);
        assert.containsNone(list,'.o_selected_row');
        awaittestUtils.dom.click(list.$('.o_data_row:first.o_boolean_toggle'));
        assert.notOk(list.$('.o_data_row:first.o_boolean_toggleinput')[0].checked);
        assert.containsNone(list,'.o_selected_row');
        assert.verifySteps(['write:false']);

        //togglethebooleanvalueafterswitchingtherowinedition
        assert.containsNone(list,'.o_selected_row');
        awaittestUtils.dom.click(list.$('.o_data_row.o_data_cell:first'));
        assert.containsOnce(list,'.o_selected_row');
        awaittestUtils.dom.click(list.$('.o_selected_row.o_boolean_toggle'));
        assert.containsOnce(list,'.o_selected_row');
        assert.verifySteps([]);

        //save
        awaittestUtils.dom.click(list.$('.o_list_button_save'));
        assert.containsNone(list,'.o_selected_row');
        assert.verifySteps(['write:true']);

        list.destroy();
    });

    QUnit.test('basicoperationsforeditablelistrenderer',asyncfunction(assert){
        assert.expect(2);

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<treeeditable="bottom"><fieldname="foo"/><fieldname="bar"/></tree>',
        });

        var$td=list.$('td:not(.o_list_record_selector)').first();
        assert.doesNotHaveClass($td.parent(),'o_selected_row',"tdshouldnotbeineditmode");
        awaittestUtils.dom.click($td);
        assert.hasClass($td.parent(),'o_selected_row',"tdshouldbeineditmode");
        list.destroy();
    });

    QUnit.test('editablelist:addalineanddiscard',asyncfunction(assert){
        assert.expect(11);

        testUtils.mock.patch(basicFields.FieldChar,{
            destroy:function(){
                assert.step('destroy');
                this._super.apply(this,arguments);
            },
        });

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<treeeditable="bottom"><fieldname="foo"/><fieldname="bar"/></tree>',
            domain:[['foo','=','yop']],
        });


        assert.containsN(list,'tbodytr',4,
            "listshouldcontain4rows");
        assert.containsOnce(list,'.o_data_row',
            "listshouldcontainonerecord(andthus3emptyrows)");

        assert.strictEqual(cpHelpers.getPagerValue(list),'1-1',
            "pagershouldbecorrect");

        awaittestUtils.dom.click(list.$buttons.find('.o_list_button_add'));

        assert.containsN(list,'tbodytr',4,
            "listshouldstillcontain4rows");
        assert.containsN(list,'.o_data_row',2,
            "listshouldcontaintworecord(andthus2emptyrows)");
        assert.strictEqual(cpHelpers.getPagerValue(list),'1-2',
            "pagershouldbecorrect");

        awaittestUtils.dom.click(list.$buttons.find('.o_list_button_discard'));

        assert.containsN(list,'tbodytr',4,
            "listshouldstillcontain4rows");
        assert.containsOnce(list,'.o_data_row',
            "listshouldcontainonerecord(andthus3emptyrows)");
        assert.strictEqual(cpHelpers.getPagerValue(list),'1-1',
            "pagershouldbecorrect");
        assert.verifySteps(['destroy'],
            "shouldhavedestroyedthewidgetoftheremovedline");

        testUtils.mock.unpatch(basicFields.FieldChar);
        list.destroy();
    });

    QUnit.test('fieldchangesaretriggeredcorrectly',asyncfunction(assert){
        assert.expect(2);

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<treeeditable="bottom"><fieldname="foo"/><fieldname="bar"/></tree>',
        });
        var$td=list.$('td:not(.o_list_record_selector)').first();

        varn=0;
        testUtils.mock.intercept(list,"field_changed",function(){
            n+=1;
        });
        awaittestUtils.dom.click($td);
        awaittestUtils.fields.editInput($td.find('input'),'abc');
        assert.strictEqual(n,1,"field_changedshouldhavebeentriggered");
        awaittestUtils.dom.click(list.$('td:not(.o_list_record_selector)').eq(2));
        assert.strictEqual(n,1,"field_changedshouldnothavebeentriggered");
        list.destroy();
    });

    QUnit.test('editablelistview:basiccharfieldedition',asyncfunction(assert){
        assert.expect(4);

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<treeeditable="bottom"><fieldname="foo"/><fieldname="bar"/></tree>',
        });

        var$td=list.$('td:not(.o_list_record_selector)').first();
        awaittestUtils.dom.click($td);
        awaittestUtils.fields.editInput($td.find('input'),'abc');
        assert.strictEqual($td.find('input').val(),'abc',"charfieldhasbeeneditedcorrectly");

        var$next_row_td=list.$('tbodytr:eq(1)td:not(.o_list_record_selector)').first();
        awaittestUtils.dom.click($next_row_td);
        assert.strictEqual(list.$('td:not(.o_list_record_selector)').first().text(),'abc',
            'changesshouldbesavedcorrectly');
        assert.doesNotHaveClass(list.$('tbodytr').first(),'o_selected_row',
            'savedrowshouldbeinreadonlymode');
        assert.strictEqual(this.data.foo.records[0].foo,'abc',
            "theeditionshouldhavebeenproperlysaved");
        list.destroy();
    });

    QUnit.test('editablelistview:savedatawhenlistsortingineditmode',asyncfunction(assert){
        assert.expect(3);

        this.data.foo.fields.foo.sortable=true;

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<treeeditable="bottom"><fieldname="foo"/></tree>',
            mockRPC:function(route,args){
                if(args.method==='write'){
                    assert.deepEqual(args.args,[[1],{foo:'xyz'}],
                        "shouldcorrectlysavetheeditedrecord");
                }
                returnthis._super.apply(this,arguments);
            },
        });

        awaittestUtils.dom.click(list.$('.o_data_cell:first'));
        awaittestUtils.fields.editInput(list.$('input[name="foo"]'),'xyz');
        awaittestUtils.dom.click(list.$('.o_column_sortable'));

        assert.hasClass(list.$('.o_data_row:first'),'o_selected_row',
            "firstrowshouldstillbeinedition");

        awaittestUtils.dom.click(list.$buttons.find('.o_list_button_save'));
        assert.doesNotHaveClass(list.$buttons,'o-editing',
            "listbuttonsshouldbebacktotheirreadonlymode");

        list.destroy();
    });

    QUnit.test('editablelistview:checkthatcontrolpanelbuttonsareupdatingwhengroupbyapplied',asyncfunction(assert){
        assert.expect(4);

        this.data.foo.fields.foo={string:"Foo",type:"char",required:true};

        varactionManager=awaitcreateActionManager({
            actions:[{
               id:11,
               name:'PartnersAction11',
               res_model:'foo',
               type:'ir.actions.act_window',
               views:[[3,'list']],
               search_view_id:[9,'search'],
            }],
            archs: {
               'foo,3,list':'<treeeditable="top"><fieldname="display_name"/><fieldname="foo"/></tree>',

               'foo,9,search':'<search>'+
                                    '<filterstring="candle"name="itsName"context="{\'group_by\':\'foo\'}"/>' +
                                    '</search>',
            },
            data:this.data,
        });

        awaitactionManager.doAction(11);
        awaittestUtils.dom.click(actionManager.$('.o_list_button_add'));

        assert.isNotVisible(actionManager.$('.o_list_button_add'),
            "createbuttonshouldbeinvisible");
        assert.isVisible(actionManager.$('.o_list_button_save'),"savebuttonshouldbevisible");

        awaittestUtils.dom.click(actionManager.$('.o_dropdown_toggler_btn:contains("GroupBy")'));
        awaittestUtils.dom.click(actionManager.$('.o_group_by_menu.o_menu_itema:contains("candle")'));

        assert.isNotVisible(actionManager.$('.o_list_button_add'),"createbuttonshouldbeinvisible");
        assert.isNotVisible(actionManager.$('.o_list_button_save'),
            "savebuttonshouldbeinvisibleafterapplyinggroupby");

        actionManager.destroy();
    });

    QUnit.test('listviewnotgroupable',asyncfunction(assert){
        assert.expect(2);

        constsearchMenuTypesOriginal=ListView.prototype.searchMenuTypes;
        ListView.prototype.searchMenuTypes=['filter','favorite'];

        constlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:`
                <treeeditable="top">
                    <fieldname="display_name"/>
                    <fieldname="foo"/>
                </tree>
            `,
            archs:{
                'foo,false,search':`
                    <search>
                        <filtercontext="{'group_by':'foo'}"name="foo"/>
                    </search>
                `,
            },
            mockRPC:function(route,args){
                if(args.method==='read_group'){
                    thrownewError("Shouldnotdoaread_groupRPC");
                }
                returnthis._super.apply(this,arguments);
            },
            context:{search_default_foo:1,},
        });

        assert.containsNone(list,'.o_control_paneldiv.o_search_optionsdiv.o_group_by_menu',
        "thereshouldnotbegroupbymenu");
        assert.deepEqual(cpHelpers.getFacetTexts(list),[]);

        list.destroy();
        ListView.prototype.searchMenuTypes=searchMenuTypesOriginal;
    });

    QUnit.test('selectionchangesaretriggeredcorrectly',asyncfunction(assert){
        assert.expect(8);

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<tree><fieldname="foo"/><fieldname="bar"/></tree>',
        });
        var$tbody_selector=list.$('tbody.o_list_record_selectorinput').first();
        var$thead_selector=list.$('thead.o_list_record_selectorinput');

        varn=0;
        testUtils.mock.intercept(list,"selection_changed",function(){
            n+=1;
        });

        //tbodycheckboxclick
        testUtils.dom.click($tbody_selector);
        assert.strictEqual(n,1,"selection_changedshouldhavebeentriggered");
        assert.ok($tbody_selector.is(':checked'),"selectioncheckboxshouldbechecked");
        testUtils.dom.click($tbody_selector);
        assert.strictEqual(n,2,"selection_changedshouldhavebeentriggered");
        assert.ok(!$tbody_selector.is(':checked'),"selectioncheckboxshouldn'tbechecked");

        //headcheckboxclick
        testUtils.dom.click($thead_selector);
        assert.strictEqual(n,3,"selection_changedshouldhavebeentriggered");
        assert.containsN(list,'tbody.o_list_record_selectorinput:checked',
            list.$('tbodytr').length,"allselectioncheckboxesshouldbechecked");

        testUtils.dom.click($thead_selector);
        assert.strictEqual(n,4,"selection_changedshouldhavebeentriggered");

        assert.containsNone(list,'tbody.o_list_record_selectorinput:checked',
                            "noselectioncheckboxshouldbechecked");
        list.destroy();
    });

    QUnit.test('Rowselectioncheckboxcanbetoggledbyclickingonthecell',asyncfunction(assert){
        assert.expect(9);

        constlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<tree><fieldname="foo"/><fieldname="bar"/></tree>',
        });

        testUtils.mock.intercept(list,"selection_changed",function(ev){
            assert.step(ev.data.selection.length.toString());
        });

        testUtils.dom.click(list.$('tbody.o_list_record_selector:first'));
        assert.containsOnce(list,'tbody.o_list_record_selectorinput:checked');
        testUtils.dom.click(list.$('tbody.o_list_record_selector:first'));
        assert.containsNone(list,'.o_list_record_selectorinput:checked');

        testUtils.dom.click(list.$('thead.o_list_record_selector'));
        assert.containsN(list,'.o_list_record_selectorinput:checked',5);
        testUtils.dom.click(list.$('thead.o_list_record_selector'));
        assert.containsNone(list,'.o_list_record_selectorinput:checked');

        assert.verifySteps(['1','0','4','0']);

        list.destroy();
    });

    QUnit.test('headselectoristoggledbytheotherselectors',asyncfunction(assert){
        assert.expect(6);

        constlist=awaitcreateView({
            arch:'<tree><fieldname="foo"/><fieldname="bar"/></tree>',
            data:this.data,
            groupBy:['bar'],
            model:'foo',
            View:ListView,
        });

        assert.ok(!list.$('thead.o_list_record_selectorinput')[0].checked,
            "Headselectorshouldbeunchecked");

        awaittestUtils.dom.click(list.$('.o_group_header:first()'));
        awaittestUtils.dom.click(list.$('thead.o_list_record_selectorinput'));

        assert.containsN(list,'tbody.o_list_record_selectorinput:checked',
            3,"Allvisiblecheckboxesshouldbechecked");

        awaittestUtils.dom.click(list.$('.o_group_header:last()'));

        assert.ok(!list.$('thead.o_list_record_selectorinput')[0].checked,
            "Headselectorshouldbeunchecked");

        awaittestUtils.dom.click(list.$('tbody.o_list_record_selectorinput:last()'));

        assert.ok(list.$('thead.o_list_record_selectorinput')[0].checked,
            "Headselectorshouldbechecked");

        awaittestUtils.dom.click(list.$('tbody.o_list_record_selector:first()input'));

        assert.ok(!list.$('thead.o_list_record_selectorinput')[0].checked,
            "Headselectorshouldbeunchecked");

        awaittestUtils.dom.click(list.$('.o_group_header:first()'));

        assert.ok(list.$('thead.o_list_record_selectorinput')[0].checked,
            "Headselectorshouldbechecked");

        list.destroy();
    });

    QUnit.test('selectionboxisproperlydisplayed(singlepage)',asyncfunction(assert){
        assert.expect(11);

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<tree><fieldname="foo"/><fieldname="bar"/></tree>',
        });

        assert.containsN(list,'.o_data_row',4);
        assert.containsNone(list.$('.o_cp_buttons'),'.o_list_selection_box');

        //selectarecord
        awaittestUtils.dom.click(list.$('.o_data_row:first.o_list_record_selectorinput'));
        assert.containsOnce(list.$('.o_cp_buttons'),'.o_list_selection_box');
        assert.containsNone(list.$('.o_list_selection_box'),'.o_list_select_domain');
        assert.strictEqual(list.$('.o_list_selection_box').text().trim(),'1selected');

        //selectallrecordsoffirstpage
        awaittestUtils.dom.click(list.$('thead.o_list_record_selectorinput'));
        assert.containsOnce(list.$('.o_cp_buttons'),'.o_list_selection_box');
        assert.containsNone(list.$('.o_list_selection_box'),'.o_list_select_domain');
        assert.strictEqual(list.$('.o_list_selection_box').text().trim(),'4selected');

        //unselectarecord
        awaittestUtils.dom.click(list.$('.o_data_row:nth(1).o_list_record_selectorinput'));
        assert.containsOnce(list.$('.o_cp_buttons'),'.o_list_selection_box');
        assert.containsNone(list.$('.o_list_selection_box'),'.o_list_select_domain');
        assert.strictEqual(list.$('.o_list_selection_box').text().trim(),'3selected');

        list.destroy();
    });

    QUnit.test('selectionboxisproperlydisplayed(multipages)',asyncfunction(assert){
        assert.expect(10);

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<treelimit="3"><fieldname="foo"/><fieldname="bar"/></tree>',
        });

        assert.containsN(list,'.o_data_row',3);
        assert.containsNone(list.$('.o_cp_buttons'),'.o_list_selection_box');

        //selectarecord
        awaittestUtils.dom.click(list.$('.o_data_row:first.o_list_record_selectorinput'));
        assert.containsOnce(list.$('.o_cp_buttons'),'.o_list_selection_box');
        assert.containsNone(list.$('.o_list_selection_box'),'.o_list_select_domain');
        assert.strictEqual(list.$('.o_list_selection_box').text().trim(),'1selected');

        //selectallrecordsoffirstpage
        awaittestUtils.dom.click(list.$('thead.o_list_record_selectorinput'));
        assert.containsOnce(list.$('.o_cp_buttons'),'.o_list_selection_box');
        assert.containsOnce(list.$('.o_list_selection_box'),'.o_list_select_domain');
        assert.strictEqual(list.$('.o_list_selection_box').text().replace(/\s+/g,'').trim(),
            '3selectedSelectall4');

        //selectalldomain
        awaittestUtils.dom.click(list.$('.o_list_selection_box.o_list_select_domain'));
        assert.containsOnce(list.$('.o_cp_buttons'),'.o_list_selection_box');
        assert.strictEqual(list.$('.o_list_selection_box').text().trim(),'All4selected');

        list.destroy();
    });

    QUnit.test('selectionboxisremovedaftermultirecordedition',asyncfunction(assert){
        assert.expect(6);

        constlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<treemulti_edit="1"><fieldname="foo"/><fieldname="bar"/></tree>',
        });

        assert.containsN(list,'.o_data_row',4,
            "thereshouldbe4records");
        assert.containsNone(list.$('.o_cp_buttons'),'.o_list_selection_box',
            "listselectionboxshouldnotbedisplayed");

        //selectallrecords
        awaittestUtils.dom.click(list.$('thead.o_list_record_selectorinput'));
        assert.containsOnce(list.$('.o_cp_buttons'),'.o_list_selection_box',
            "listselectionboxshouldbedisplayed");
        assert.containsN(list,'.o_data_row.o_list_record_selectorinput:checked',4,
            "all4recordsshouldbeselected");

        //editselectedrecords
        awaittestUtils.dom.click(list.$('.o_data_row:eq(0).o_data_cell:eq(0)'));
        awaittestUtils.fields.editInput(list.$('.o_field_widget[name=foo]'),'legion');
        awaittestUtils.dom.click($('.modal-dialogbutton.btn-primary'));
        assert.containsNone(list.$('.o_cp_buttons'),'.o_list_selection_box',
            "listselectionboxshouldnotbedisplayed");
        assert.containsNone(list,'.o_data_row.o_list_record_selectorinput:checked',
            "norecordsshouldbeselected");

        list.destroy();
    });

    QUnit.test('selectionisresetonreload',asyncfunction(assert){
        assert.expect(8);

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<tree>'+
                    '<fieldname="foo"/>'+
                    '<fieldname="int_field"sum="Sum"/>'+
                '</tree>',
        });

        assert.containsNone(list.$('.o_cp_buttons'),'.o_list_selection_box');
        assert.strictEqual(list.$('tfoottd:nth(2)').text(),'32',
            "totalshouldbe32(norecordselected)");

        //selectfirstrecord
        var$firstRowSelector=list.$('tbody.o_list_record_selectorinput').first();
        testUtils.dom.click($firstRowSelector);
        assert.ok($firstRowSelector.is(':checked'),"firstrowshouldbeselected");
        assert.containsOnce(list.$('.o_cp_buttons'),'.o_list_selection_box');
        assert.strictEqual(list.$('tfoottd:nth(2)').text(),'10',
            "totalshouldbe10(firstrecordselected)");

        //reload
        awaitlist.reload();
        $firstRowSelector=list.$('tbody.o_list_record_selectorinput').first();
        assert.notOk($firstRowSelector.is(':checked'),
            "firstrowshouldnolongerbeselected");
        assert.containsNone(list.$('.o_cp_buttons'),'.o_list_selection_box');
        assert.strictEqual(list.$('tfoottd:nth(2)').text(),'32',
            "totalshouldbe32(nomorerecordselected)");

        list.destroy();
    });

    QUnit.test('selectioniskeptonrenderwithoutreload',asyncfunction(assert){
        assert.expect(10);

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            groupBy:['foo'],
            viewOptions:{hasActionMenus:true},
            arch:'<tree>'+
                    '<fieldname="foo"/>'+
                    '<fieldname="int_field"sum="Sum"/>'+
                '</tree>',
        });

        assert.containsNone(list.el,'div.o_control_panel.o_cp_action_menus');
        assert.containsNone(list.$('.o_cp_buttons'),'.o_list_selection_box');

        //openblipgroupingandcheckalllines
        awaittestUtils.dom.click(list.$('.o_group_header:contains("blip(2)")'));
        awaittestUtils.dom.click(list.$('.o_data_row:firstinput'));
        assert.containsOnce(list.el,'div.o_control_panel.o_cp_action_menus');
        assert.containsOnce(list.$('.o_cp_buttons'),'.o_list_selection_box');

        //openyopgroupingandverifybliparestillchecked
        awaittestUtils.dom.click(list.$('.o_group_header:contains("yop(1)")'));
        assert.containsOnce(list,'.o_data_rowinput:checked',
            "openingagroupingdoesnotuncheckothers");
        assert.containsOnce(list.el,'div.o_control_panel.o_cp_action_menus');
        assert.containsOnce(list.$('.o_cp_buttons'),'.o_list_selection_box');

        //closeandopenblipgroupingandverifyblipareunchecked
        awaittestUtils.dom.click(list.$('.o_group_header:contains("blip(2)")'));
        awaittestUtils.dom.click(list.$('.o_group_header:contains("blip(2)")'));
        assert.containsNone(list,'.o_data_rowinput:checked',
            "openingandclosingagroupinguncheckitselements");
        assert.containsNone(list.el,'div.o_control_panel.o_cp_action_menus');
        assert.containsNone(list.$('.o_cp_buttons'),'.o_list_selection_box');

        list.destroy();
    });

    QUnit.test('aggregatesarecomputedcorrectly',asyncfunction(assert){
        assert.expect(4);

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<treeeditable="bottom"><fieldname="foo"/><fieldname="int_field"sum="Sum"/></tree>',
        });
        var$tbody_selectors=list.$('tbody.o_list_record_selectorinput');
        var$thead_selector=list.$('thead.o_list_record_selectorinput');

        assert.strictEqual(list.$('tfoottd:nth(2)').text(),"32","totalshouldbe32");

        testUtils.dom.click($tbody_selectors.first());
        testUtils.dom.click($tbody_selectors.last());
        assert.strictEqual(list.$('tfoottd:nth(2)').text(),"6",
                        "totalshouldbe6asfirstandlastrecordsareselected");

        testUtils.dom.click($thead_selector);
        assert.strictEqual(list.$('tfoottd:nth(2)').text(),"32",
                        "totalshouldbe32asallrecordsareselected");

        //Let'supdatetheviewtodislayNOrecords
        awaitlist.update({domain:['&',['bar','=',false],['int_field','>',0]]});
        assert.strictEqual(list.$('tfoottd:nth(2)').text(),"0","totalshouldhavebeenrecomputedto0");

        list.destroy();
    });

    QUnit.test('aggregatesarecomputedcorrectlyingroupedlists',asyncfunction(assert){
        assert.expect(4);

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            groupBy:['m2o'],
            arch:'<treeeditable="bottom"><fieldname="foo"/><fieldname="int_field"sum="Sum"/></tree>',
        });

        var$groupHeader1=list.$('.o_group_header').filter(function(index,el){
            return$(el).data('group').res_id===1;
        });
        var$groupHeader2=list.$('.o_group_header').filter(function(index,el){
            return$(el).data('group').res_id===2;
        });
        assert.strictEqual($groupHeader1.find('td:last()').text(),"23","firstgrouptotalshouldbe23");
        assert.strictEqual($groupHeader2.find('td:last()').text(),"9","secondgrouptotalshouldbe9");
        assert.strictEqual(list.$('tfoottd:last()').text(),"32","totalshouldbe32");

        awaittestUtils.dom.click($groupHeader1);
        awaittestUtils.dom.click(list.$('tbody.o_list_record_selectorinput').first());
        assert.strictEqual(list.$('tfoottd:last()').text(),"10",
                        "totalshouldbe10asfirstrecordoffirstgroupisselected");
        list.destroy();
    });

    QUnit.test('aggregatesareupdatedwhenalineisedited',asyncfunction(assert){
        assert.expect(2);

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<treeeditable="bottom"><fieldname="int_field"sum="Sum"/></tree>',
        });

        assert.strictEqual(list.$('td[title="Sum"]').text(),"32","currenttotalshouldbe32");

        awaittestUtils.dom.click(list.$('tr.o_data_rowtd.o_data_cell').first());
        awaittestUtils.fields.editInput(list.$('td.o_data_cellinput'),"15");

        assert.strictEqual(list.$('td[title="Sum"]').text(),"37",
            "currenttotalshouldnowbe37");
        list.destroy();
    });

    QUnit.test('aggregatesareformattedaccordingtofieldwidget',asyncfunction(assert){
        assert.expect(1);

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<tree>'+
                    '<fieldname="foo"/>'+
                    '<fieldname="qux"widget="float_time"sum="Sum"/>'+
                '</tree>',
        });

        assert.strictEqual(list.$('tfoottd:nth(2)').text(),'19:24',
            "totalshouldbeformattedasafloat_time");

        list.destroy();
    });

    QUnit.test('aggregatesdigitscanbesetwithdigitsfieldattribute',asyncfunction(assert){
        assert.expect(2);

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<tree>'+
                    '<fieldname="amount"widget="monetary"sum="Sum"digits="[69,3]"/>'+
                '</tree>',
        });

        assert.strictEqual(list.$('.o_data_rowtd:nth(1)').text(),'1200.00',
            "fieldshouldstillbeformattedbasedoncurrency");
        assert.strictEqual(list.$('tfoottd:nth(1)').text(),'2000.000',
            "aggregatesmonetaryusedigitsattributeifavailable");

        list.destroy();
    });

    QUnit.test('groupscanbesortedonaggregates',asyncfunction(assert){
        assert.expect(10);
        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            groupBy:['foo'],
            arch:'<treeeditable="bottom"><fieldname="foo"/><fieldname="int_field"sum="Sum"/></tree>',
            mockRPC:function(route,args){
                if(args.method==='web_read_group'){
                    assert.step(args.kwargs.orderby||'defaultorder');
                }
                returnthis._super.apply(this,arguments);
            },
        });

        assert.strictEqual(list.$('tbody.o_list_number').text(),'10517',
            "initialordershouldbe10,5,17");
        assert.strictEqual(list.$('tfoottd:last()').text(),'32',"totalshouldbe32");

        awaittestUtils.dom.click(list.$('.o_column_sortable'));
        assert.strictEqual(list.$('tfoottd:last()').text(),'32',"totalshouldstillbe32");
        assert.strictEqual(list.$('tbody.o_list_number').text(),'51017',
            "ordershouldbe5,10,17");

        awaittestUtils.dom.click(list.$('.o_column_sortable'));
        assert.strictEqual(list.$('tbody.o_list_number').text(),'17105',
            "initialordershouldbe17,10,5");
        assert.strictEqual(list.$('tfoottd:last()').text(),'32',"totalshouldstillbe32");

        assert.verifySteps(['defaultorder','int_fieldASC','int_fieldDESC']);

        list.destroy();
    });

    QUnit.test('groupscannotbesortedonnon-aggregablefields',asyncfunction(assert){
        assert.expect(6);
        this.data.foo.fields.sort_field={string:"sortable_field",type:"sting",sortable:true,default:"value"};
        _.each(this.data.records,function(elem){
            elem.sort_field="value"+elem.id;
        });
        this.data.foo.fields.foo.sortable=true;
        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            groupBy:['foo'],
            arch:'<treeeditable="bottom"><fieldname="foo"/><fieldname="int_field"/><fieldname="sort_field"/></tree>',
            mockRPC:function(route,args){
                if(args.method==='web_read_group'){
                    assert.step(args.kwargs.orderby||'defaultorder');
                }
                returnthis._super.apply(this,arguments);
            },
        });
        //wecannotsortbysort_fieldsinceitdoesn'thaveagroup_operator
        awaittestUtils.dom.click(list.$('.o_column_sortable:eq(2)'));
        //wecansortbyint_fieldsinceithasagroup_operator
        awaittestUtils.dom.click(list.$('.o_column_sortable:eq(1)'));
        //wekeeppreviousorder
        awaittestUtils.dom.click(list.$('.o_column_sortable:eq(2)'));
        //wecansortonfoosincewearegrouppedbyfoo+previousorder
        awaittestUtils.dom.click(list.$('.o_column_sortable:eq(0)'));

        assert.verifySteps([
            'defaultorder',
            'defaultorder',
            'int_fieldASC',
            'int_fieldASC',
            'fooASC,int_fieldASC'
        ]);

        list.destroy();
    });

    QUnit.test('properlyapplyonchangeinsimplecase',asyncfunction(assert){
        assert.expect(2);

        this.data.foo.onchanges={
            foo:function(obj){
                obj.int_field=obj.foo.length+1000;
            },
        };
        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<treeeditable="top"><fieldname="foo"/><fieldname="int_field"/></tree>',
        });

        var$foo_td=list.$('td:not(.o_list_record_selector)').first();
        var$int_field_td=list.$('td:not(.o_list_record_selector)').eq(1);

        assert.strictEqual($int_field_td.text(),'10',"shouldcontaininitialvalue");

        awaittestUtils.dom.click($foo_td);
        awaittestUtils.fields.editInput($foo_td.find('input'),'tralala');

        assert.strictEqual($int_field_td.find('input').val(),"1007",
                        "shouldcontaininputwithonchangeapplied");
        list.destroy();
    });

    QUnit.test('columnwidthshouldnotchangewhenswitchingmode',asyncfunction(assert){
        assert.expect(4);

        //Warning:thistestiscssdependant
        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<treeeditable="top">'+
                        '<fieldname="foo"/>'+
                        '<fieldname="int_field"readonly="1"/>'+
                        '<fieldname="m2o"/>'+
                        '<fieldname="m2m"widget="many2many_tags"/>'+
                    '</tree>',
        });

        varstartWidths=_.pluck(list.$('theadth'),'offsetWidth');
        varstartWidth=list.$('table').addBack('table').width();

        //starteditionoffirstrow
        awaittestUtils.dom.click(list.$('td:not(.o_list_record_selector)').first());

        vareditionWidths=_.pluck(list.$('theadth'),'offsetWidth');
        vareditionWidth=list.$('table').addBack('table').width();

        //leaveedition
        awaittestUtils.dom.click(list.$buttons.find('.o_list_button_save'));

        varreadonlyWidths=_.pluck(list.$('theadth'),'offsetWidth');
        varreadonlyWidth=list.$('table').addBack('table').width();

        assert.strictEqual(editionWidth,startWidth,
            "tableshouldhavekeptthesamewidthwhenswitchingfromreadonlytoeditmode");
        assert.deepEqual(editionWidths,startWidths,
            "widthofcolumnsshouldremainunchangedwhenswitchingfromreadonlytoeditmode");
        assert.strictEqual(readonlyWidth,editionWidth,
            "tableshouldhavekeptthesamewidthwhenswitchingfromedittoreadonlymode");
        assert.deepEqual(readonlyWidths,editionWidths,
            "widthofcolumnsshouldremainunchangedwhenswitchingfromedittoreadonlymode");

        list.destroy();
    });

    QUnit.test('columnwidthsshoulddependonthecontentwhenthereisdata',asyncfunction(assert){
        assert.expect(1);

        this.data.foo.records[0].foo='Someveryverylongvalueforacharfield';

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<treeeditable="top">'+
                        '<fieldname="bar"/>'+
                        '<fieldname="foo"/>'+
                        '<fieldname="int_field"/>'+
                        '<fieldname="qux"/>'+
                        '<fieldname="date"/>'+
                        '<fieldname="datetime"/>'+
                    '</tree>',
            viewOptions:{
                limit:2,
            },
        });
        varwidthPage1=list.$(`th[data-name=foo]`)[0].offsetWidth;

        awaitcpHelpers.pagerNext(list);

        varwidthPage2=list.$(`th[data-name=foo]`)[0].offsetWidth;
        assert.ok(widthPage1>widthPage2,
            'columnwidthsshouldbecomputeddynamicallyaccordingtothecontent');

        list.destroy();
    });

    QUnit.test('widthofsomeofthefieldsshouldbehardcodedifnodata',asyncfunction(assert){
        constassertions=[
            {field:'bar',expected:70,type:'Boolean'},
            {field:'int_field',expected:74,type:'Integer'},
            {field:'qux',expected:92,type:'Float'},
            {field:'date',expected:92,type:'Date'},
            {field:'datetime',expected:146,type:'Datetime'},
            {field:'amount',expected:104,type:'Monetary'},
        ];
        assert.expect(9);

        this.data.foo.records=[];
        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<treeeditable="top">'+
                        '<fieldname="bar"/>'+
                        '<fieldname="foo"/>'+
                        '<fieldname="int_field"/>'+
                        '<fieldname="qux"/>'+
                        '<fieldname="date"/>'+
                        '<fieldname="datetime"/>'+
                        '<fieldname="amount"/>'+
                        '<fieldname="currency_id"width="25px"/>'+
                    '</tree>',
        });

        assert.containsNone(list,'.o_resize',"Thereshouldn'tbeanyresizehandleifnodata");
        assertions.forEach(a=>{
            assert.strictEqual(list.$(`th[data-name="${a.field}"]`)[0].offsetWidth,a.expected,
                `Field${a.type}shouldhaveafixedwidthof${a.expected}pixels`);
        });
        assert.strictEqual(list.$('th[data-name="foo"]')[0].style.width,'100%',
            "Charfieldshouldoccupytheremainingspace");
        assert.strictEqual(list.$('th[data-name="currency_id"]')[0].offsetWidth,25,
            'Currencyfieldshouldhaveafixedwidthof25px(seearch)');

        list.destroy();
    });

    QUnit.test('widthofsomefieldsshouldbehardcodedifnodata,andlistinitiallyinvisible',asyncfunction(assert){
        constassertions=[
            {field:'bar',expected:70,type:'Boolean'},
            {field:'int_field',expected:74,type:'Integer'},
            {field:'qux',expected:92,type:'Float'},
            {field:'date',expected:92,type:'Date'},
            {field:'datetime',expected:146,type:'Datetime'},
            {field:'amount',expected:104,type:'Monetary'},
        ];
        assert.expect(12);

        this.data.foo.fields.foo_o2m={string:"FooO2M",type:"one2many",relation:"foo"};
        constform=awaitcreateView({
            View:FormView,
            model:'foo',
            data:this.data,
            res_id:1,
            viewOptions:{mode:'edit'},
            arch:`<form>
                    <sheet>
                        <notebook>
                            <pagestring="Page1"></page>
                            <pagestring="Page2">
                                <fieldname="foo_o2m">
                                    <treeeditable="bottom">
                                        <fieldname="bar"/>
                                        <fieldname="foo"/>
                                        <fieldname="int_field"/>
                                        <fieldname="qux"/>
                                        <fieldname="date"/>
                                        <fieldname="datetime"/>
                                        <fieldname="amount"/>
                                        <fieldname="currency_id"width="25px"/>
                                    </tree>
                                </field>
                            </page>
                        </notebook>
                    </sheet>
                </form>`,
        });

        assert.isNotVisible(form.$('.o_field_one2many'));

        awaittestUtils.dom.click(form.$('.nav-item:last-child.nav-link'));

        assert.isVisible(form.$('.o_field_one2many'));

        assert.containsNone(form,'.o_field_one2many.o_resize',
            "Thereshouldn'tbeanyresizehandleifnodata");
        assertions.forEach(a=>{
            assert.strictEqual(form.$(`.o_field_one2manyth[data-name="${a.field}"]`)[0].offsetWidth,a.expected,
                `Field${a.type}shouldhaveafixedwidthof${a.expected}pixels`);
        });
        assert.strictEqual(form.$('.o_field_one2manyth[data-name="foo"]')[0].style.width,'100%',
            "Charfieldshouldoccupytheremainingspace");
        assert.strictEqual(form.$('th[data-name="currency_id"]')[0].offsetWidth,25,
            'Currencyfieldshouldhaveafixedwidthof25px(seearch)');
        assert.strictEqual(form.el.querySelector('.o_list_record_remove_header').style.width,'32px');

        form.destroy();
    });

    QUnit.test('emptyeditablelistwiththehandlewidgetandnocontenthelp',asyncfunction(assert){
        assert.expect(4);

        //norecordsforthefoomodel
        this.data.foo.records=[];

        constlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:`<treeeditable="bottom">
                    <fieldname="int_field"widget="handle"/>
                    <fieldname="foo"/>
                </tree>`,
            viewOptions:{
                action:{
                    help:'<pclass="hello">clicktoaddafoo</p>'
                }
            },
        });

        //ashelpisbeingprovidedintheaction,tablewon'tberendereduntilarecordexists
        assert.containsNone(list,'.o_list_table',"thereshouldnotbeanyrecordsintheview.");
        assert.containsOnce(list,'.o_view_nocontent',"shouldhavenocontenthelp");

        //clickoncreatebutton
        awaittestUtils.dom.click(list.$('.o_list_button_add'));
        consthandleWidgetMinWidth="33px";
        consthandleWidgetHeader=list.$('thead>tr>th.o_handle_cell');
        assert.strictEqual(handleWidgetHeader.css('min-width'),handleWidgetMinWidth,
            "Whilecreatingfirstrecord,min-widthshouldbeappliedtohandlewidget.");

        //creatingonerecord
        awaittestUtils.fields.editInput(list.$("tr.o_selected_rowinput[name='foo']"),'test_foo');
        awaittestUtils.dom.click(list.$('.o_list_button_save'));
        assert.strictEqual(handleWidgetHeader.css('min-width'),handleWidgetMinWidth,
            "Aftercreationofthefirstrecord,min-widthofthehandlewidgetshouldremainasitis");

        list.destroy();
    });

    QUnit.test('editablelist:overflowingtable',asyncfunction(assert){
        assert.expect(1);

        this.data.bar={
            fields:{
                titi:{string:"Smallchar",type:"char",sortable:true},
                grosminet:{string:"Beegchar",type:"char",sortable:true},
            },
            records:[
                {
                    id:1,
                    titi:"Tinytext",
                    grosminet:
                        //Justwanttomakesurethatthetableisoverflowed
                        `Loremipsumdolorsitamet,consecteturadipiscingelit.
                        Donecestmassa,gravidaegetdapibusac,eleifendegetlibero.
                        Suspendissefeugiatsedmassaeleifendvestibulum.Sedtincidunt
                        velitsedlacinialacinia.Nuncinfermentumnunc.Vestibulumante
                        ipsumprimisinfaucibusorciluctusetultricesposuerecubilia
                        Curae;Nullamutnisiaestornaremolestienonvulputateorci.
                        Nuncpharetraportasemper.Maurisdictumeunullaapulvinar.Duis
                        eleifendodioidligulaconguesollicitudin.Curabiturquisaliquet
                        nunc,utaliquetenim.Suspendissemalesuadafelisnonmetus
                        efficituraliquet.`,
                },
            ],
        };
        constlist=awaitcreateView({
            arch:`
                <treeeditable="top">
                    <fieldname="titi"/>
                    <fieldname="grosminet"widget="char"/>
                </tree>`,
            data:this.data,
            model:'bar',
            View:ListView,
        });

        assert.strictEqual(list.$('table').width(),list.$('.o_list_view').width(),
            "Tableshouldnotbestretchedbyitscontent");

        list.destroy();
    });

    QUnit.test('editablelist:overflowingtable(3columns)',asyncfunction(assert){
        assert.expect(4);

        constlongText=`Loremipsumdolorsitamet,consecteturadipiscingelit.
                        Donecestmassa,gravidaegetdapibusac,eleifendegetlibero.
                        Suspendissefeugiatsedmassaeleifendvestibulum.Sedtincidunt
                        velitsedlacinialacinia.Nuncinfermentumnunc.Vestibulumante
                        ipsumprimisinfaucibusorciluctusetultricesposuerecubilia
                        Curae;Nullamutnisiaestornaremolestienonvulputateorci.
                        Nuncpharetraportasemper.Maurisdictumeunullaapulvinar.Duis
                        eleifendodioidligulaconguesollicitudin.Curabiturquisaliquet
                        nunc,utaliquetenim.Suspendissemalesuadafelisnonmetus
                        efficituraliquet.`;

        this.data.bar={
            fields:{
                titi:{string:"Smallchar",type:"char",sortable:true},
                grosminet1:{string:"Beegchar1",type:"char",sortable:true},
                grosminet2:{string:"Beegchar2",type:"char",sortable:true},
                grosminet3:{string:"Beegchar3",type:"char",sortable:true},
            },
            records:[{
                id:1,
                titi:"Tinytext",
                grosminet1:longText,
                grosminet2:longText+longText,
                grosminet3:longText+longText+longText,
            }],
        };
        constlist=awaitcreateView({
            arch:`
                <treeeditable="top">
                    <fieldname="titi"/>
                    <fieldname="grosminet1"class="large"/>
                    <fieldname="grosminet3"class="large"/>
                    <fieldname="grosminet2"class="large"/>
                </tree>`,
            data:this.data,
            model:'bar',
            View:ListView,
        });

        assert.strictEqual(list.$('table').width(),list.$('.o_list_view').width());
        constlargeCells=list.$('.o_data_cell.large');
        assert.ok(Math.abs(largeCells[0].offsetWidth-largeCells[1].offsetWidth)<=1);
        assert.ok(Math.abs(largeCells[1].offsetWidth-largeCells[2].offsetWidth)<=1);
        assert.ok(list.$('.o_data_cell:not(.large)')[0].offsetWidth<largeCells[0].offsetWidth);

        list.destroy();
    });

    QUnit.test('editablelist:listviewinaninitiallyunselectednotebookpage',asyncfunction(assert){
        assert.expect(5);

        this.data.foo.records=[{id:1,o2m:[1]}];
        this.data.bar={
            fields:{
                titi:{string:"Smallchar",type:"char",sortable:true},
                grosminet:{string:"Beegchar",type:"char",sortable:true},
            },
            records:[
                {
                    id:1,
                    titi:"Tinytext",
                    grosminet:
                        'Loremipsumdolorsitamet,consecteturadipiscingelit.'+
                        'Utatnisicongue,facilisisnequenec,pulvinarnunc.'+
                        'Vivamusaclectusvelit.',
                },
            ],
        };
        constform=awaitcreateView({
            View:FormView,
            model:'foo',
            data:this.data,
            res_id:1,
            viewOptions:{mode:'edit'},
            arch:'<form>'+
                    '<sheet>'+
                        '<notebook>'+
                            '<pagestring="Page1"></page>'+
                            '<pagestring="Page2">'+
                                '<fieldname="o2m">'+
                                    '<treeeditable="bottom">'+
                                        '<fieldname="titi"/>'+
                                        '<fieldname="grosminet"/>'+
                                    '</tree>'+
                                '</field>'+
                            '</page>'+
                        '</notebook>'+
                    '</sheet>'+
                '</form>',
        });

        const[titi,grosminet]=form.el.querySelectorAll('.tab-pane:last-childth');
        constone2many=form.el.querySelector('.o_field_one2many');

        assert.isNotVisible(one2many,
            "One2manyfieldshouldbehidden");
        assert.strictEqual(titi.style.width,"",
            "widthofsmallcharshouldnotbesetyet");
        assert.strictEqual(grosminet.style.width,"",
            "widthoflargecharshouldalsonotbeset");

        awaittestUtils.dom.click(form.el.querySelector('.nav-item:last-child.nav-link'));

        assert.isVisible(one2many,
            "One2manyfieldshouldbevisible");
        assert.ok(
            titi.style.width.split('px')[0]>80&&
            grosminet.style.width.split('px')[0]>700,
            "listhasbeencorrectlyfrozenafterbeingvisible");

        form.destroy();
    });

    QUnit.test('editablelist:listviewhiddenbyaninvisiblemodifier',asyncfunction(assert){
        assert.expect(5);

        this.data.foo.records=[{id:1,bar:true,o2m:[1]}];
        this.data.bar={
            fields:{
                titi:{string:"Smallchar",type:"char",sortable:true},
                grosminet:{string:"Beegchar",type:"char",sortable:true},
            },
            records:[
                {
                    id:1,
                    titi:"Tinytext",
                    grosminet:
                        'Loremipsumdolorsitamet,consecteturadipiscingelit.'+
                        'Utatnisicongue,facilisisnequenec,pulvinarnunc.'+
                        'Vivamusaclectusvelit.',
                },
            ],
        };
        varform=awaitcreateView({
            View:FormView,
            model:'foo',
            data:this.data,
            res_id:1,
            viewOptions:{mode:'edit'},
            arch:'<form>'+
                    '<sheet>'+
                        '<fieldname="bar"/>'+
                        '<fieldname="o2m"attrs="{\'invisible\':[(\'bar\',\'=\',True)]}">'+
                            '<treeeditable="bottom">'+
                                '<fieldname="titi"/>'+
                                '<fieldname="grosminet"/>'+
                            '</tree>'+
                        '</field>'+
                    '</sheet>'+
                '</form>',
        });

        const[titi,grosminet]=form.el.querySelectorAll('th');
        constone2many=form.el.querySelector('.o_field_one2many');

        assert.isNotVisible(one2many,
            "One2manyfieldshouldbehidden");
        assert.strictEqual(titi.style.width,"",
            "widthofsmallcharshouldnotbesetyet");
        assert.strictEqual(grosminet.style.width,"",
            "widthoflargecharshouldalsonotbeset");

        awaittestUtils.dom.click(form.el.querySelector('.o_field_booleaninput'));

        assert.isVisible(one2many,
            "One2manyfieldshouldbevisible");
        assert.ok(
            titi.style.width.split('px')[0]>80&&
            grosminet.style.width.split('px')[0]>700,
            "listhasbeencorrectlyfrozenafterbeingvisible");

        form.destroy();
    });

    QUnit.test('editablelist:updatingliststatewhileinvisible',asyncfunction(assert){
        assert.expect(2);

        this.data.foo.onchanges={
            bar:function(obj){
                obj.o2m=[[5],[0,null,{display_name:"Whatever"}]];
            },
        };
        varform=awaitcreateView({
            View:FormView,
            model:'foo',
            data:this.data,
            res_id:1,
            viewOptions:{mode:'edit'},
            arch:'<form>'+
                    '<sheet>'+
                        '<fieldname="bar"/>'+
                        '<notebook>'+
                            '<pagestring="Page1"></page>'+
                            '<pagestring="Page2">'+
                                '<fieldname="o2m">'+
                                    '<treeeditable="bottom">'+
                                        '<fieldname="display_name"/>'+
                                    '</tree>'+
                                '</field>'+
                            '</page>'+
                        '</notebook>'+
                    '</sheet>'+
                '</form>',
        });

        awaittestUtils.dom.click(form.$('.o_field_booleaninput'));

        assert.strictEqual(form.el.querySelector('th').style.width,"",
            "Columnheadershouldbeinitiallyunfrozen");

        awaittestUtils.dom.click(form.$('.nav-item:last().nav-link'));

        assert.notEqual(form.el.querySelector('th').style.width,"",
            "Columnheadershouldhavebeenfrozen");

        form.destroy();
    });

    QUnit.test('emptylist:statewithnamelessandstringlessbuttons',asyncfunction(assert){
        assert.expect(2);

        this.data.foo.records=[];
        constlist=awaitcreateView({
            arch:`
                <tree>
                    <fieldname="foo"/>
                    <buttonstring="choucroute"/>
                    <buttonicon="fa-heart"/>
                </tree>`,
            data:this.data,
            model:'foo',
            View:ListView,
        });

        assert.strictEqual(list.el.querySelector('th[data-name="foo"]').style.width,'50%',
            "Fieldcolumnshouldbefrozen");
        assert.strictEqual(list.el.querySelector('th:last-child').style.width,'50%',
            "Buttonscolumnshouldbefrozen");

        list.destroy();
    });

    QUnit.test('editablelist:unnamedcolumnscannotberesized',asyncfunction(assert){
        assert.expect(2);

        this.data.foo.records=[{id:1,o2m:[1]}];
        this.data.bar.records=[{id:1,display_name:"Oui"}];
        varform=awaitcreateView({
            View:FormView,
            model:'foo',
            data:this.data,
            res_id:1,
            viewOptions:{mode:'edit'},
            arch:'<form>'+
                    '<sheet>'+
                        '<fieldname="o2m">'+
                            '<treeeditable="top">'+
                                '<fieldname="display_name"/>'+
                                '<buttonname="the_button"icon="fa-heart"/>'+
                            '</tree>'+
                        '</field>'+
                    '</sheet>'+
                '</form>',
        });

        const[charTh,buttonTh]=form.$('.o_field_one2manyth');
        constthRect=charTh.getBoundingClientRect();
        constresizeRect=charTh.getElementsByClassName('o_resize')[0].getBoundingClientRect();

        assert.strictEqual(thRect.x+thRect.width,resizeRect.x+resizeRect.width,
            "Firstresizehandleshouldbeattachedattheendofthefirstheader");
        assert.containsNone(buttonTh,'.o_resize',
            "Columnswithoutnameshouldnothavearesizehandle");

        form.destroy();
    });

    QUnit.test('editablelistview,clickonm2odropdowndonotcloseeditablerow',asyncfunction(assert){
        assert.expect(2);

        constlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<treestring="Phonecalls"editable="top">'+
                '<fieldname="m2o"/>'+
                '</tree>',
        });

        awaittestUtils.dom.click(list.$buttons.find('.o_list_button_add'));
        awaittestUtils.dom.click(list.$('.o_selected_row.o_data_cell.o_field_many2oneinput'));
        const$dropdown=list.$('.o_selected_row.o_data_cell.o_field_many2oneinput').autocomplete('widget');
        awaittestUtils.dom.click($dropdown);
        assert.containsOnce(list,'.o_selected_row',"shouldstillhaveeditablerow");

        awaittestUtils.dom.click($dropdown.find("li:first"));
        assert.containsOnce(list,'.o_selected_row',"shouldstillhaveeditablerow");

        list.destroy();
    });

    QUnit.test('widthofsomeofthefieldsshouldbehardcodedifnodata(groupedcase)',asyncfunction(assert){
        constassertions=[
            {field:'bar',expected:70,type:'Boolean'},
            {field:'int_field',expected:74,type:'Integer'},
            {field:'qux',expected:92,type:'Float'},
            {field:'date',expected:92,type:'Date'},
            {field:'datetime',expected:146,type:'Datetime'},
            {field:'amount',expected:104,type:'Monetary'},
        ];
        assert.expect(9);

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<treeeditable="top">'+
                        '<fieldname="bar"/>'+
                        '<fieldname="foo"/>'+
                        '<fieldname="int_field"/>'+
                        '<fieldname="qux"/>'+
                        '<fieldname="date"/>'+
                        '<fieldname="datetime"/>'+
                        '<fieldname="amount"/>'+
                        '<fieldname="currency_id"width="25px"/>'+
                    '</tree>',
            groupBy:['int_field'],
        });

        assert.containsNone(list,'.o_resize',"Thereshouldn'tbeanyresizehandleifnodata");
        assertions.forEach(a=>{
            assert.strictEqual(list.$(`th[data-name="${a.field}"]`)[0].offsetWidth,a.expected,
                `Field${a.type}shouldhaveafixedwidthof${a.expected}pixels`);
        });
        assert.strictEqual(list.$('th[data-name="foo"]')[0].style.width,'100%',
            "Charfieldshouldoccupytheremainingspace");
        assert.strictEqual(list.$('th[data-name="currency_id"]')[0].offsetWidth,25,
            "Currencyfieldshouldhaveafixedwidthof25px(seearch)");

        list.destroy();
    });

    QUnit.test('columnwidthshoulddependonthewidget',asyncfunction(assert){
        assert.expect(1);

        this.data.foo.records=[];//thewidthheuristiconlyapplieswhentherearenorecords
        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<treeeditable="top">'+
                        '<fieldname="datetime"widget="date"/>'+
                        '<fieldname="text"/>'+
                    '</tree>',
        });

        assert.strictEqual(list.$('th[data-name="datetime"]')[0].offsetWidth,92,
            "shouldbetheoptimalwidthtodisplayadate,notadatetime");

        list.destroy();
    });

    QUnit.test('columnwidthsarekeptwhenaddingfirstrecord',asyncfunction(assert){
        assert.expect(2);

        this.data.foo.records=[];//inthisscenario,westartwithnorecords
        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<treeeditable="top">'+
                        '<fieldname="datetime"/>'+
                        '<fieldname="text"/>'+
                    '</tree>',
        });

        varwidth=list.$('th[data-name="datetime"]')[0].offsetWidth;

        awaittestUtils.dom.click(list.$buttons.find('.o_list_button_add'));

        assert.containsOnce(list,'.o_data_row');
        assert.strictEqual(list.$('th[data-name="datetime"]')[0].offsetWidth,width);

        list.destroy();
    });

    QUnit.test('columnwidthsarekeptwheneditingarecord',asyncfunction(assert){
        assert.expect(3);

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<treeeditable="bottom">'+
                        '<fieldname="datetime"/>'+
                        '<fieldname="text"/>'+
                    '</tree>',
        });

        varwidth=list.$('th[data-name="datetime"]')[0].offsetWidth;

        awaittestUtils.dom.click(list.$('.o_data_row:eq(0).o_data_cell:eq(1)'));
        assert.containsOnce(list,'.o_selected_row');

        varlongVal='Loremipsumdolorsitamet,consecteturadipiscingelit.Sedblandit,'+
            'justonectinciduntfeugiat,mijustosuscipitlibero,sitamettempusipsumpurus'+
            'bibendumest.';
        awaittestUtils.fields.editInput(list.$('.o_field_widget[name=text]'),longVal);
        awaittestUtils.dom.click(list.$buttons.find('.o_list_button_save'));

        assert.containsNone(list,'.o_selected_row');
        assert.strictEqual(list.$('th[data-name="datetime"]')[0].offsetWidth,width);

        list.destroy();
    });

    QUnit.test('columnwidthsarekeptwhenswitchingrecordsinedition',asyncfunction(assert){
        assert.expect(4);

        constlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:`<treeeditable="bottom">
                    <fieldname="m2o"/>
                    <fieldname="text"/>
                </tree>`,
        });

        constwidth=list.$('th[data-name="m2o"]')[0].offsetWidth;

        awaittestUtils.dom.click(list.$('.o_data_row:first.o_data_cell:first'));

        assert.hasClass(list.$('.o_data_row:first'),'o_selected_row');
        assert.strictEqual(list.$('th[data-name="m2o"]')[0].offsetWidth,width);

        awaittestUtils.dom.click(list.$('.o_data_row:nth(1).o_data_cell:first'));

        assert.hasClass(list.$('.o_data_row:nth(1)'),'o_selected_row');
        assert.strictEqual(list.$('th[data-name="m2o"]')[0].offsetWidth,width);

        list.destroy();
    });

    QUnit.test('columnwidthsarere-computedonwindowresize',asyncfunction(assert){
        assert.expect(2);

        testUtils.mock.patch(ListRenderer,{
            RESIZE_DELAY:0,
        });

        this.data.foo.records[0].text='Loremipsumdolorsitamet,consecteturadipiscingelit.'+
            'Sedblandit,justonectinciduntfeugiat,mijustosuscipitlibero,sitamettempus'+
            'ipsumpurusbibendumest.';
        constlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:`<treeeditable="bottom">
                        <fieldname="datetime"/>
                        <fieldname="text"/>
                    </tree>`,
        });

        constinitialTextWidth=list.$('th[data-name="text"]')[0].offsetWidth;
        constselectorWidth=list.$('th.o_list_record_selector')[0].offsetWidth;

        //simulateawindowresize
        list.$el.width(`${list.$el.width()/2}px`);
        core.bus.trigger('resize');
        awaittestUtils.nextTick();

        constpostResizeTextWidth=list.$('th[data-name="text"]')[0].offsetWidth;
        constpostResizeSelectorWidth=list.$('th.o_list_record_selector')[0].offsetWidth;
        assert.ok(postResizeTextWidth<initialTextWidth);
        assert.strictEqual(selectorWidth,postResizeSelectorWidth);

        testUtils.mock.unpatch(ListRenderer);
        list.destroy();
    });

    QUnit.test('columnswithanabsolutewidtharenevernarrowerthanthatwidth',asyncfunction(assert){
        assert.expect(2);

        this.data.foo.records[0].text='Loremipsumdolorsitamet,consecteturadipiscingelit,'+
            'seddoeiusmodtemporincididuntutlaboreetdoloremagnaaliqua.Utenimadminim'+
            'veniam,quisnostrudexercitationullamcolaborisnisiutaliquipexeacommodo'+
            'consequat.Duisauteiruredolorinreprehenderitinvoluptatevelitessecillum'+
            'doloreeufugiatnullapariatur.Excepteursintoccaecatcupidatatnonproident,'+
            'suntinculpaquiofficiadeseruntmollitanimidestlaborum';
        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<treeeditable="bottom">'+
                        '<fieldname="datetime"/>'+
                        '<fieldname="int_field"width="200px"/>'+
                        '<fieldname="text"/>'+
                    '</tree>',
        });

        assert.strictEqual(list.$('th[data-name="datetime"]')[0].offsetWidth,146);
        assert.strictEqual(list.$('th[data-name="int_field"]')[0].offsetWidth,200);

        list.destroy();
    });

    QUnit.test('listviewwithdata:textcolumnsarenotcrushed',asyncfunction(assert){
        assert.expect(2);

        constlongText='Loremipsumdolorsitamet,consecteturadipiscingelit,seddo'+
            'eiusmodtemporincididuntutlaboreetdoloremagnaaliqua.Utenimadminim'+
            'veniam,quisnostrudexercitationullamcolaborisnisiutaliquipexeacommodo'+
            'consequat.Duisauteiruredolorinreprehenderitinvoluptatevelitessecillum'+
            'doloreeufugiatnullapariatur.Excepteursintoccaecatcupidatatnonproident,'+
            'suntinculpaquiofficiadeseruntmollitanimidestlaborum';
        this.data.foo.records[0].foo=longText;
        this.data.foo.records[0].text=longText;
        this.data.foo.records[1].foo="shorttext";
        this.data.foo.records[1].text="shorttext";
        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<tree><fieldname="foo"/><fieldname="text"/></tree>',
        });

        constfoo=list.el.querySelector('th[data-name="foo"]');
        constfooWidth=Math.ceil(foo.getBoundingClientRect().width);

        consttext=list.el.querySelector('th[data-name="text"]');
        consttextWidth=Math.ceil(text.getBoundingClientRect().width);

        assert.ok(Math.abs(fooWidth-textWidth)<=1,"bothcolumnsshouldhavebeengiventhesamewidth");

        constfirstRowHeight=list.$('.o_data_row:nth(0)')[0].offsetHeight;
        constsecondRowHeight=list.$('.o_data_row:nth(1)')[0].offsetHeight;
        assert.ok(firstRowHeight>secondRowHeight,
            "inthefirstrow,the(long)textfieldshouldbeproperlydisplayedonseverallines");

        list.destroy();
    });

    QUnit.test("buttoninalistviewwithadefaultrelativewidth",asyncfunction(assert){
        assert.expect(1);

        constlist=awaitcreateView({
            arch:`
            <tree>
                <fieldname="foo"/>
                <buttonname="the_button"icon="fa-heart"width="0.1"/>
            </tree>`,
            data:this.data,
            model:'foo',
            View:ListView,
        });

        assert.strictEqual(list.el.querySelector('.o_data_cellbutton').style.width,"",
            "widthattributeshouldnotchangetheCSSstyle");

        list.destroy();
    });

    QUnit.test("buttoncolumnsinalistviewdon'thaveamaxwidth",asyncfunction(assert){
        assert.expect(2);

        testUtils.mock.patch(ListRenderer,{
            RESIZE_DELAY:0,
        });

        //setalongfoovalues.t.thecolumncanbesqueezed
        this.data.foo.records[0].foo='Loremipsumdolorsitamet';
        constlist=awaitcreateView({
            arch:`
                <tree>
                    <fieldname="foo"/>
                    <buttonname="b1"string="DoThis"/>
                    <buttonname="b2"string="DoThat"/>
                    <buttonname="b3"string="OrRatherDoSomethingElse"/>
                </tree>`,
            data:this.data,
            model:'foo',
            View:ListView,
        });

        //simulateawindowresize(buttonscolumnwidthshouldnotbesqueezed)
        list.$el.width('300px');
        core.bus.trigger('resize');
        awaittestUtils.nextTick();

        assert.strictEqual(list.$('th:nth(1)').css('max-width'),'92px',
            "max-widthshouldbesetoncolumnfoototheminimumcolumnwidth(92px)");
        assert.strictEqual(list.$('th:nth(2)').css('max-width'),'100%',
            "nomax-widthshouldbeharcodedonthebuttonscolumn");

        testUtils.mock.unpatch(ListRenderer);
        list.destroy();
    });

    QUnit.test('columnwidthsarekeptwheneditingmultiplerecords',asyncfunction(assert){
        assert.expect(4);

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<treemulti_edit="1">'+
                        '<fieldname="datetime"/>'+
                        '<fieldname="text"/>'+
                    '</tree>',
        });

        varwidth=list.$('th[data-name="datetime"]')[0].offsetWidth;

        //selecttworecordsandedit
        awaittestUtils.dom.click(list.$('.o_data_row:eq(0).o_list_record_selectorinput'));
        awaittestUtils.dom.click(list.$('.o_data_row:eq(1).o_list_record_selectorinput'));
        awaittestUtils.dom.click(list.$('.o_data_row:eq(0).o_data_cell:eq(1)'));

        assert.containsOnce(list,'.o_selected_row');
        varlongVal='Loremipsumdolorsitamet,consecteturadipiscingelit.Sedblandit,'+
            'justonectinciduntfeugiat,mijustosuscipitlibero,sitamettempusipsumpurus'+
            'bibendumest.';
        awaittestUtils.fields.editInput(list.$('.o_field_widget[name=text]'),longVal);
        assert.containsOnce(document.body,'.modal');
        awaittestUtils.dom.click($('.modal.btn-primary'));

        assert.containsNone(list,'.o_selected_row');
        assert.strictEqual(list.$('th[data-name="datetime"]')[0].offsetWidth,width);

        list.destroy();
    });

    QUnit.test('rowheightandwidthshouldnotchangewhenswitchingmode',asyncfunction(assert){
        //Warning:thistestiscssdependant
        assert.expect(5);

        varmultiLang=_t.database.multi_lang;
        _t.database.multi_lang=true;

        this.data.foo.fields.foo.translate=true;
        this.data.foo.fields.boolean={type:'boolean',string:'Bool'};
        varcurrencies={};
        _.each(this.data.res_currency.records,function(currency){
            currencies[currency.id]=currency;
        });

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<treeeditable="top">'+
                        '<fieldname="foo"required="1"/>'+
                        '<fieldname="int_field"readonly="1"/>'+
                        '<fieldname="boolean"/>'+
                        '<fieldname="date"/>'+
                        '<fieldname="text"/>'+
                        '<fieldname="amount"/>'+
                        '<fieldname="currency_id"invisible="1"/>'+
                        '<fieldname="m2o"/>'+
                        '<fieldname="m2m"widget="many2many_tags"/>'+
                    '</tree>',
            session:{
                currencies:currencies,
            },
        });

        //thewidthishardcodedtomakesurewehavethesamecondition
        //betweendebugmodeandnondebugmode
        list.$el.width('1200px');
        varstartHeight=list.$('.o_data_row:first').outerHeight();
        varstartWidth=list.$('.o_data_row:first').outerWidth();

        //starteditionoffirstrow
        awaittestUtils.dom.click(list.$('.o_data_row:first>td:not(.o_list_record_selector)').first());
        assert.hasClass(list.$('.o_data_row:first'),'o_selected_row');
        vareditionHeight=list.$('.o_data_row:first').outerHeight();
        vareditionWidth=list.$('.o_data_row:first').outerWidth();

        //leaveedition
        awaittestUtils.dom.click(list.$buttons.find('.o_list_button_save'));
        varreadonlyHeight=list.$('.o_data_row:first').outerHeight();
        varreadonlyWidth=list.$('.o_data_row:first').outerWidth();

        assert.strictEqual(startHeight,editionHeight);
        assert.strictEqual(startHeight,readonlyHeight);
        assert.strictEqual(startWidth,editionWidth);
        assert.strictEqual(startWidth,readonlyWidth);

        _t.database.multi_lang=multiLang;
        list.destroy();
    });

    QUnit.test('fieldsaretranslatableinlistview',asyncfunction(assert){
        assert.expect(3);

        varmultiLang=_t.database.multi_lang;
        _t.database.multi_lang=true;
        this.data.foo.fields.foo.translate=true;

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            mockRPC:function(route,args){
                if(route==="/web/dataset/call_button"&&args.method==='translate_fields'){
                    returnPromise.resolve({
                        domain:[],
                        context:{search_default_name:'foo,foo'},
                    });
                }
                if(route==="/web/dataset/call_kw/res.lang/get_installed"){
                    returnPromise.resolve([["en_US","English"],["fr_BE","Frenglish"]]);
                }
                returnthis._super.apply(this,arguments);
            },
            arch:'<treeeditable="top">'+
                        '<fieldname="foo"required="1"/>'+
                    '</tree>',
        });

        awaittestUtils.dom.click(list.$('.o_data_row:first>td:not(.o_list_record_selector)').first());
        assert.hasClass(list.$('.o_data_row:first'),'o_selected_row');

        awaittestUtils.dom.click(list.$('input.o_field_translate+span.o_field_translate'));
        awaittestUtils.nextTick();

        assert.containsOnce($('body'),'.o_translation_dialog');
        assert.containsN($('.o_translation_dialog'),'.translation>input.o_field_char',2,
            'modalshouldhave2languagestotranslate');

        _t.database.multi_lang=multiLang;
        list.destroy();
    });

    QUnit.test('fieldsaretranslatableinmulti-editablelistview',asyncfunction(assert){
        assert.expect(1);
        varmultiLang=_t.database.multi_lang;
        _t.database.multi_lang=true;
        this.data.foo.fields.foo.translate=true;

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            session:{
                user_context:{lang:'en_US'},
            },
            mockRPC:function(route,args){
                if(route==="/web/dataset/call_button"&&args.method==='translate_fields'){
                    returnPromise.resolve({
                        domain:[],
                        context:{search_default_name:'foo,foo'},
                    });
                }
                if(route==="/web/dataset/call_kw/res.lang/get_installed"){
                    returnPromise.resolve([["en_US","English"],["fr_BE","Frenglish"]]);
                }
                returnthis._super.apply(this,arguments);
            },
            arch:'<treemulti_edit="1">'+
                        '<fieldname="foo"required="1"/>'+
                    '</tree>',
        });

        awaittestUtils.dom.click(list.$('.o_data_row:first.o_list_record_selectorinput').first());
        awaittestUtils.nextTick();
        awaittestUtils.dom.click(list.$('.o_data_row:first.o_list_char'));
        awaittestUtils.nextTick();
        awaittestUtils.dom.click(list.$('input.o_field_translate+span.o_field_translate'));
        awaittestUtils.nextTick();

        awaittestUtils.fields.editInput($('.o_translation_dialoginput:first'),'bla_');
        awaittestUtils.nextTick();

        awaittestUtils.modal.clickButton('Save');
        assert.strictEqual($('.o_data_row:first.o_list_char').text(),'bla_');

        _t.database.multi_lang=multiLang;
        list.destroy();
    });


    QUnit.test('longwordsintextcellsshouldbreakintosmallerlines',asyncfunction(assert){
        assert.expect(2);

        this.data.foo.records[0].text="a";
        this.data.foo.records[1].text="pneumonoultramicroscopicsilicovolcanoconiosis";//longestenglishwordIcouldfind

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<tree><fieldname="text"/></tree>',
        });

        //Intentionallysetthetablewidthtoasmallsize
        list.$('table').width('100px');
        list.$('th:last').width('100px');
        varshortText=list.$('.o_data_row:eq(0)td:last')[0].clientHeight;
        varlongText=list.$('.o_data_row:eq(1)td:last')[0].clientHeight;
        varemptyText=list.$('.o_data_row:eq(2)td:last')[0].clientHeight;

        assert.strictEqual(shortText,emptyText,
            "Shortwordshouldnotchangetheheightofthecell");
        assert.ok(longText>emptyText,
            "Longwordshouldchangetheheightofthecell");

        list.destroy();
    });

    QUnit.test('deletingonerecord',asyncfunction(assert){
        assert.expect(5);

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            viewOptions:{hasActionMenus:true},
            arch:'<tree><fieldname="foo"/></tree>',
        });


        assert.containsNone(list.el,'div.o_control_panel.o_cp_action_menus');
        assert.containsN(list,'tbodytd.o_list_record_selector',4,"shouldhave4records");

        awaittestUtils.dom.click(list.$('tbodytd.o_list_record_selector:firstinput'));

        assert.containsOnce(list.el,'div.o_control_panel.o_cp_action_menus');

        awaitcpHelpers.toggleActionMenu(list);
        awaitcpHelpers.toggleMenuItem(list,"Delete");
        assert.hasClass($('body'),'modal-open','bodyshouldhavemodal-openclsss');

        awaittestUtils.dom.click($('body.modalbuttonspan:contains(Ok)'));

        assert.containsN(list,'tbodytd.o_list_record_selector',3,"shouldhave3records");
        list.destroy();
    });

    QUnit.test('deleteallrecordsmatchingthedomain',asyncfunction(assert){
        assert.expect(6);

        this.data.foo.records.push({id:5,bar:true,foo:"xxx"});

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<treelimit="2"><fieldname="foo"/></tree>',
            domain:[['bar','=',true]],
            mockRPC:function(route,args){
                if(args.method==='unlink'){
                    assert.deepEqual(args.args[0],[1,2,3,5]);
                }
                returnthis._super.apply(this,arguments);
            },
            services:{
                notification:NotificationService.extend({
                    notify:function(){
                        thrownewError('shouldnotdisplayanotification');
                    },
                }),
            },
            viewOptions:{
                hasActionMenus:true,
            },
        });

        assert.containsNone(list,'div.o_control_panel.o_cp_action_menus');
        assert.containsN(list,'tbodytd.o_list_record_selector',2,"shouldhave2records");

        awaittestUtils.dom.click(list.$('thead.o_list_record_selectorinput'));

        assert.containsOnce(list,'div.o_control_panel.o_cp_action_menus');
        assert.containsOnce(list,'.o_list_selection_box.o_list_select_domain');

        awaittestUtils.dom.click(list.$('.o_list_selection_box.o_list_select_domain'));
        awaitcpHelpers.toggleActionMenu(list);
        awaitcpHelpers.toggleMenuItem(list,"Delete");

        assert.strictEqual($('.modal').length,1,'aconfirmmodalshouldbedisplayed');
        awaittestUtils.dom.click($('.modal-footer.btn-primary'));

        list.destroy();
    });

    QUnit.test('deleteallrecordsmatchingthedomain(limitreached)',asyncfunction(assert){
        assert.expect(8);

        this.data.foo.records.push({id:5,bar:true,foo:"xxx"});
        this.data.foo.records.push({id:6,bar:true,foo:"yyy"});

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<treelimit="2"><fieldname="foo"/></tree>',
            domain:[['bar','=',true]],
            mockRPC:function(route,args){
                if(args.method==='unlink'){
                    assert.deepEqual(args.args[0],[1,2,3,5]);
                }
                returnthis._super.apply(this,arguments);
            },
            services:{
                notification:NotificationService.extend({
                    notify:function(){
                        assert.step('notify');
                    },
                }),
            },
            session:{
                active_ids_limit:4,
            },
            viewOptions:{
                hasActionMenus:true,
            },
        });


        assert.containsNone(list,'div.o_control_panel.o_cp_action_menus');
        assert.containsN(list,'tbodytd.o_list_record_selector',2,"shouldhave2records");

        awaittestUtils.dom.click(list.$('thead.o_list_record_selectorinput'));

        assert.containsOnce(list,'div.o_control_panel.o_cp_action_menus');
        assert.containsOnce(list,'.o_list_selection_box.o_list_select_domain');

        awaittestUtils.dom.click(list.$('.o_list_selection_box.o_list_select_domain'));
        awaitcpHelpers.toggleActionMenu(list);
        awaitcpHelpers.toggleMenuItem(list,"Delete");

        assert.strictEqual($('.modal').length,1,'aconfirmmodalshouldbedisplayed');
        awaittestUtils.dom.click($('.modal-footer.btn-primary'));

        assert.verifySteps(['notify']);

        list.destroy();
    });

    QUnit.test('archivingonerecord',asyncfunction(assert){
        assert.expect(12);

        //addactivefieldonfoomodelandmakeallrecordsactive
        this.data.foo.fields.active={string:'Active',type:'boolean',default:true};

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            viewOptions:{hasActionMenus:true},
            arch:'<tree><fieldname="foo"/></tree>',
            mockRPC:function(route){
                assert.step(route);
                if(route==='/web/dataset/call_kw/foo/action_archive'){
                    this.data.foo.records[0].active=false;
                    returnPromise.resolve();
                }
                returnthis._super.apply(this,arguments);
            },
        });


        assert.containsNone(list.el,'div.o_control_panel.o_cp_action_menus');
        assert.containsN(list,'tbodytd.o_list_record_selector',4,"shouldhave4records");

        awaittestUtils.dom.click(list.$('tbodytd.o_list_record_selector:firstinput'));

        assert.containsOnce(list.el,'div.o_control_panel.o_cp_action_menus');

        assert.verifySteps(['/web/dataset/search_read']);
        awaitcpHelpers.toggleActionMenu(list);
        awaitcpHelpers.toggleMenuItem(list,"Archive");
        assert.strictEqual($('.modal').length,1,'aconfirmmodalshouldbedisplayed');
        awaittestUtils.dom.click($('.modal-footer.btn-secondary'));
        assert.containsN(list,'tbodytd.o_list_record_selector',4,"stillshouldhave4records");

        awaitcpHelpers.toggleActionMenu(list);
        awaitcpHelpers.toggleMenuItem(list,"Archive");
        assert.strictEqual($('.modal').length,1,'aconfirmmodalshouldbedisplayed');
        awaittestUtils.dom.click($('.modal-footer.btn-primary'));
        assert.containsN(list,'tbodytd.o_list_record_selector',3,"shouldhave3records");
        assert.verifySteps(['/web/dataset/call_kw/foo/action_archive','/web/dataset/search_read']);
        list.destroy();
    });

    QUnit.test('archiveallrecordsmatchingthedomain',asyncfunction(assert){
        assert.expect(6);

        //addactivefieldonfoomodelandmakeallrecordsactive
        this.data.foo.fields.active={string:'Active',type:'boolean',default:true};
        this.data.foo.records.push({id:5,bar:true,foo:"xxx"});

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<treelimit="2"><fieldname="foo"/></tree>',
            domain:[['bar','=',true]],
            mockRPC:function(route,args){
                if(args.method==='action_archive'){
                    assert.deepEqual(args.args[0],[1,2,3,5]);
                    returnPromise.resolve();
                }
                returnthis._super.apply(this,arguments);
            },
            services:{
                notification:NotificationService.extend({
                    notify:function(){
                        thrownewError('shouldnotdisplayanotification');
                    },
                }),
            },
            viewOptions:{
                hasActionMenus:true,
            },
        });

        assert.containsNone(list,'div.o_control_panel.o_cp_action_menus');
        assert.containsN(list,'tbodytd.o_list_record_selector',2,"shouldhave2records");

        awaittestUtils.dom.click(list.$('thead.o_list_record_selectorinput'));

        assert.containsOnce(list,'div.o_control_panel.o_cp_action_menus');
        assert.containsOnce(list,'.o_list_selection_box.o_list_select_domain');

        awaittestUtils.dom.click(list.$('.o_list_selection_box.o_list_select_domain'));
        awaitcpHelpers.toggleActionMenu(list);
        awaitcpHelpers.toggleMenuItem(list,"Archive");

        assert.strictEqual($('.modal').length,1,'aconfirmmodalshouldbedisplayed');
        awaittestUtils.dom.click($('.modal-footer.btn-primary'));

        list.destroy();
    });

    QUnit.test('archiveallrecordsmatchingthedomain(limitreached)',asyncfunction(assert){
        assert.expect(8);

        //addactivefieldonfoomodelandmakeallrecordsactive
        this.data.foo.fields.active={string:'Active',type:'boolean',default:true};
        this.data.foo.records.push({id:5,bar:true,foo:"xxx"});
        this.data.foo.records.push({id:6,bar:true,foo:"yyy"});

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<treelimit="2"><fieldname="foo"/></tree>',
            domain:[['bar','=',true]],
            mockRPC:function(route,args){
                if(args.method==='action_archive'){
                    assert.deepEqual(args.args[0],[1,2,3,5]);
                    returnPromise.resolve();
                }
                returnthis._super.apply(this,arguments);
            },
            services:{
                notification:NotificationService.extend({
                    notify:function(){
                        assert.step('notify');
                    },
                }),
            },
            session:{
                active_ids_limit:4,
            },
            viewOptions:{
                hasActionMenus:true,
            },
        });


        assert.containsNone(list,'div.o_control_panel.o_cp_action_menus');
        assert.containsN(list,'tbodytd.o_list_record_selector',2,"shouldhave2records");

        awaittestUtils.dom.click(list.$('thead.o_list_record_selectorinput'));

        assert.containsOnce(list,'div.o_control_panel.o_cp_action_menus');
        assert.containsOnce(list,'.o_list_selection_box.o_list_select_domain');

        awaittestUtils.dom.click(list.$('.o_list_selection_box.o_list_select_domain'));
        awaitcpHelpers.toggleActionMenu(list);
        awaitcpHelpers.toggleMenuItem(list,"Archive");

        assert.strictEqual($('.modal').length,1,'aconfirmmodalshouldbedisplayed');
        awaittestUtils.dom.click($('.modal-footer.btn-primary'));

        assert.verifySteps(['notify']);

        list.destroy();
    });

    QUnit.test('archive/unarchivehandlesreturnedaction',asyncfunction(assert){
        assert.expect(6);

        //addactivefieldonfoomodelandmakeallrecordsactive
        this.data.foo.fields.active={string:'Active',type:'boolean',default:true};

        constactionManager=awaitcreateActionManager({
            data:this.data,
            actions:[{
                id:11,
                name:'Action11',
                res_model:'foo',
                type:'ir.actions.act_window',
                views:[[3,'list']],
                search_view_id:[9,'search'],
            }],
            archs:{
                'foo,3,list':'<tree><fieldname="foo"/></tree>',
                'foo,9,search':`
                    <search>
                        <filterstring="NotBar"name="notbar"domain="[['bar','=',False]]"/>
                    </search>`,
                'bar,false,form':'<form><fieldname="display_name"/></form>',
            },
            mockRPC:function(route,args){
                if(route==='/web/dataset/call_kw/foo/action_archive'){
                    returnPromise.resolve({
                        'type':'ir.actions.act_window',
                        'name':'ArchiveAction',
                        'res_model':'bar',
                        'view_mode':'form',
                        'target':'new',
                        'views':[[false,'form']]
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

        awaitactionManager.doAction(11);

        assert.containsNone(actionManager,'.o_cp_action_menus','sidebarshouldbeinvisible');
        assert.containsN(actionManager,'tbodytd.o_list_record_selector',4,"shouldhave4records");

        awaittestUtils.dom.click(actionManager.$('tbodytd.o_list_record_selector:firstinput'));

        assert.containsOnce(actionManager,'.o_cp_action_menus','sidebarshouldbevisible');

        awaittestUtils.dom.click(actionManager.$('.o_cp_action_menus.o_dropdown_toggler_btn:contains(Action)'));
        awaittestUtils.dom.click(actionManager.$('.o_cp_action_menusa:contains(Archive)'));
        assert.strictEqual($('.modal').length,1,'aconfirmmodalshouldbedisplayed');
        awaittestUtils.dom.click($('.modal.modal-footer.btn-primary'));
        assert.strictEqual($('.modal').length,2,'aconfirmmodalshouldbedisplayed');
        assert.strictEqual($('.modal:eq(1).modal-title').text().trim(),'ArchiveAction',
            "actionwizardshouldhavebeenopened");

        actionManager.destroy();
    });

    QUnit.test('pager(ungroupedandgroupedmode),defaultlimit',asyncfunction(assert){
        assert.expect(4);

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<tree><fieldname="foo"/><fieldname="bar"/></tree>',
            mockRPC:function(route,args){
                if(route==='/web/dataset/search_read'){
                    assert.strictEqual(args.limit,80,"defaultlimitshouldbe80inList");
                }
                returnthis._super.apply(this,arguments);
            },
        });

        assert.containsOnce(list.el,'div.o_control_panel.o_cp_pager');
        assert.strictEqual(cpHelpers.getPagerSize(list),"4","pager'ssizeshouldbe4");
        awaitlist.update({groupBy:['bar']});
        assert.strictEqual(cpHelpers.getPagerSize(list),"2","pager'ssizeshouldbe2");
        list.destroy();
    });

    QUnit.test('cansortrecordswhenclickingonheader',asyncfunction(assert){
        assert.expect(9);

        this.data.foo.fields.foo.sortable=true;

        varnbSearchRead=0;
        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<tree><fieldname="foo"/><fieldname="bar"/></tree>',
            mockRPC:function(route){
                if(route==='/web/dataset/search_read'){
                    nbSearchRead++;
                }
                returnthis._super.apply(this,arguments);
            },
        });

        assert.strictEqual(nbSearchRead,1,"shouldhavedoneonesearch_read");
        assert.ok(list.$('tbodytr:firsttd:contains(yop)').length,
            "record1shouldbefirst");
        assert.ok(list.$('tbodytr:eq(3)td:contains(blip)').length,
            "record3shouldbefirst");

        nbSearchRead=0;
        awaittestUtils.dom.click(list.$('theadth:contains(Foo)'));
        assert.strictEqual(nbSearchRead,1,"shouldhavedoneonesearch_read");
        assert.ok(list.$('tbodytr:firsttd:contains(blip)').length,
            "record3shouldbefirst");
        assert.ok(list.$('tbodytr:eq(3)td:contains(yop)').length,
            "record1shouldbefirst");

        nbSearchRead=0;
        awaittestUtils.dom.click(list.$('theadth:contains(Foo)'));
        assert.strictEqual(nbSearchRead,1,"shouldhavedoneonesearch_read");
        assert.ok(list.$('tbodytr:firsttd:contains(yop)').length,
            "record3shouldbefirst");
        assert.ok(list.$('tbodytr:eq(3)td:contains(blip)').length,
            "record1shouldbefirst");

        list.destroy();
    });

    QUnit.test('donotsortrecordswhenclickingonheaderwithnolabel',asyncfunction(assert){
        assert.expect(6);

        this.data.foo.fields.foo.sortable=true;

        letnbSearchRead=0;
        constlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<tree><fieldname="foo"nolabel="1"/><fieldname="int_field"/></tree>',
            mockRPC:function(route){
                if(route==='/web/dataset/search_read'){
                    nbSearchRead++;
                }
                returnthis._super.apply(this,arguments);
            },
        });

        assert.strictEqual(nbSearchRead,1,"shouldhavedoneonesearch_read");
        assert.strictEqual(list.$('.o_data_cell').text(),"yop10blip9gnap17blip-4");

        awaittestUtils.dom.click(list.$('theadth[data-name="int_field"]'));
        assert.strictEqual(nbSearchRead,2,"shouldhavedoneoneothersearch_read");
        assert.strictEqual(list.$('.o_data_cell').text(),"blip-4blip9yop10gnap17");

        awaittestUtils.dom.click(list.$('theadth[data-name="foo"]'));
        assert.strictEqual(nbSearchRead,2,"shouldn'thavedoneanymoresearch_read");
        assert.strictEqual(list.$('.o_data_cell').text(),"blip-4blip9yop10gnap17");

        list.destroy();
    });

    QUnit.test('usedefault_order',asyncfunction(assert){
        assert.expect(3);

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<treedefault_order="foo"><fieldname="foo"/><fieldname="bar"/></tree>',
            mockRPC:function(route,args){
                if(route==='/web/dataset/search_read'){
                    assert.strictEqual(args.sort,'fooASC',
                        "shouldcorrectlysetthesortattribute");
                }
                returnthis._super.apply(this,arguments);
            },
        });

        assert.ok(list.$('tbodytr:firsttd:contains(blip)').length,
            "record3shouldbefirst");
        assert.ok(list.$('tbodytr:eq(3)td:contains(yop)').length,
            "record1shouldbefirst");

        list.destroy();
    });

    QUnit.test('usemorecomplexdefault_order',asyncfunction(assert){
        assert.expect(3);

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<treedefault_order="foo,bardesc,int_field">'+
                    '<fieldname="foo"/><fieldname="bar"/>'+
                '</tree>',
            mockRPC:function(route,args){
                if(route==='/web/dataset/search_read'){
                    assert.strictEqual(args.sort,'fooASC,barDESC,int_fieldASC',
                        "shouldcorrectlysetthesortattribute");
                }
                returnthis._super.apply(this,arguments);
            },
        });

        assert.ok(list.$('tbodytr:firsttd:contains(blip)').length,
            "record3shouldbefirst");
        assert.ok(list.$('tbodytr:eq(3)td:contains(yop)').length,
            "record1shouldbefirst");

        list.destroy();
    });

    QUnit.test('usedefault_orderoneditabletree:sortonsave',asyncfunction(assert){
        assert.expect(8);

        this.data.foo.records[0].o2m=[1,3];

        varform=awaitcreateView({
            View:FormView,
            model:'foo',
            data:this.data,
            arch:'<form>'+
                    '<sheet>'+
                        '<fieldname="o2m">'+
                            '<treeeditable="bottom"default_order="display_name">'+
                                '<fieldname="display_name"/>'+
                            '</tree>'+
                        '</field>'+
                    '</sheet>'+
                '</form>',
            res_id:1,
        });

        awaittestUtils.form.clickEdit(form);
        assert.ok(form.$('tbodytr:firsttd:contains(Value1)').length,
            "Value1shouldbefirst");
        assert.ok(form.$('tbodytr:eq(1)td:contains(Value3)').length,
            "Value3shouldbesecond");

        var$o2m=form.$('.o_field_widget[name=o2m]');
        awaittestUtils.dom.click(form.$('.o_field_x2many_list_row_adda'));
        awaittestUtils.fields.editInput($o2m.find('.o_field_widget'),"Value2");
        assert.ok(form.$('tbodytr:firsttd:contains(Value1)').length,
            "Value1shouldbefirst");
        assert.ok(form.$('tbodytr:eq(1)td:contains(Value3)').length,
            "Value3shouldbesecond");
        assert.ok(form.$('tbodytr:eq(2)tdinput').val(),
            "Value2shouldbethird(shouldn'tbesorted)");

        awaittestUtils.form.clickSave(form);
        assert.ok(form.$('tbodytr:firsttd:contains(Value1)').length,
            "Value1shouldbefirst");
        assert.ok(form.$('tbodytr:eq(1)td:contains(Value2)').length,
            "Value2shouldbesecond(shouldbesortedaftersaving)");
        assert.ok(form.$('tbodytr:eq(2)td:contains(Value3)').length,
            "Value3shouldbethird");

        form.destroy();
    });

    QUnit.test('usedefault_orderoneditabletree:sortondemand',asyncfunction(assert){
        assert.expect(11);

        this.data.foo.records[0].o2m=[1,3];
        this.data.bar.fields={name:{string:"Name",type:"char",sortable:true}};
        this.data.bar.records[0].name="Value1";
        this.data.bar.records[2].name="Value3";

        varform=awaitcreateView({
            View:FormView,
            model:'foo',
            data:this.data,
            arch:'<form>'+
                    '<sheet>'+
                        '<fieldname="o2m">'+
                            '<treeeditable="bottom"default_order="name">'+
                                '<fieldname="name"/>'+
                            '</tree>'+
                        '</field>'+
                    '</sheet>'+
                '</form>',
            res_id:1,
        });

        awaittestUtils.form.clickEdit(form);
        assert.ok(form.$('tbodytr:firsttd:contains(Value1)').length,
            "Value1shouldbefirst");
        assert.ok(form.$('tbodytr:eq(1)td:contains(Value3)').length,
            "Value3shouldbesecond");

        var$o2m=form.$('.o_field_widget[name=o2m]');
        awaittestUtils.dom.click(form.$('.o_field_x2many_list_row_adda'));
        awaittestUtils.fields.editInput($o2m.find('.o_field_widget'),"Value2");
        assert.ok(form.$('tbodytr:firsttd:contains(Value1)').length,
            "Value1shouldbefirst");
        assert.ok(form.$('tbodytr:eq(1)td:contains(Value3)').length,
            "Value3shouldbesecond");
        assert.ok(form.$('tbodytr:eq(2)tdinput').val(),
            "Value2shouldbethird(shouldn'tbesorted)");

        awaittestUtils.dom.click(form.$('.o_form_sheet_bg'));

        awaittestUtils.dom.click($o2m.find('.o_column_sortable'));
        assert.strictEqual(form.$('tbodytr:first').text(),'Value1',
            "Value1shouldbefirst");
        assert.strictEqual(form.$('tbodytr:eq(1)').text(),'Value2',
            "Value2shouldbesecond(shouldbesortedaftersaving)");
        assert.strictEqual(form.$('tbodytr:eq(2)').text(),'Value3',
            "Value3shouldbethird");

        awaittestUtils.dom.click($o2m.find('.o_column_sortable'));
        assert.strictEqual(form.$('tbodytr:first').text(),'Value3',
            "Value3shouldbefirst");
        assert.strictEqual(form.$('tbodytr:eq(1)').text(),'Value2',
            "Value2shouldbesecond(shouldbesortedaftersaving)");
        assert.strictEqual(form.$('tbodytr:eq(2)').text(),'Value1',
            "Value1shouldbethird");

        form.destroy();
    });

    QUnit.test('usedefault_orderoneditabletree:sortondemandinpage',asyncfunction(assert){
        assert.expect(4);

        this.data.bar.fields={name:{string:"Name",type:"char",sortable:true}};

        varids=[];
        for(vari=0;i<45;i++){
            varid=4+i;
            ids.push(id);
            this.data.bar.records.push({
                id:id,
                name:"Value"+(id<10?'0':'')+id,
            });
        }
        this.data.foo.records[0].o2m=ids;

        varform=awaitcreateView({
            View:FormView,
            model:'foo',
            data:this.data,
            arch:'<form>'+
                    '<sheet>'+
                        '<fieldname="o2m">'+
                            '<treeeditable="bottom"default_order="name">'+
                                '<fieldname="name"/>'+
                            '</tree>'+
                        '</field>'+
                    '</sheet>'+
                '</form>',
            res_id:1,
        });

        awaitcpHelpers.pagerNext('.o_field_widget[name=o2m]');
        assert.strictEqual(form.$('tbodytr:first').text(),'Value44',
            "record44shouldbefirst");
        assert.strictEqual(form.$('tbodytr:eq(4)').text(),'Value48',
            "record48shouldbelast");

        awaittestUtils.dom.click(form.$('.o_column_sortable'));
        assert.strictEqual(form.$('tbodytr:first').text(),'Value08',
            "record48shouldbefirst");
        assert.strictEqual(form.$('tbodytr:eq(4)').text(),'Value04',
            "record44shouldbefirst");

        form.destroy();
    });

    QUnit.test('candisplaybuttonineditmode',asyncfunction(assert){
        assert.expect(2);

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<treeeditable="bottom">'+
                    '<fieldname="foo"/>'+
                    '<buttonname="notafield"type="object"icon="fa-asterisk"class="o_yeah"/>'+
                '</tree>',
        });
        assert.containsN(list,'tbodybutton[name=notafield]',4);
        assert.containsN(list,'tbodybutton[name=notafield].o_yeah',4,"classo_yeahshouldbesetonthefourbutton");
        list.destroy();
    });

    QUnit.test('candisplayalistwithamany2manyfield',asyncfunction(assert){
        assert.expect(3);

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<tree>'+
                    '<fieldname="m2m"/>'+
                '</tree>',
            mockRPC:function(route,args){
                assert.step(route);
                returnthis._super(route,args);
            },
        });
        assert.verifySteps(['/web/dataset/search_read'],"shouldhavedone1search_read");
        assert.ok(list.$('td:contains(3records)').length,
            "shouldhaveatdwithcorrectformattedvalue");
        list.destroy();
    });

    QUnit.test('listwithgroup_by_no_leafflagincontext',asyncfunction(assert){
        assert.expect(1);

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<tree><fieldname="foo"/></tree>',
            context:{
                group_by_no_leaf:true,
            }
        });

        assert.containsNone(list,'.o_list_buttons',"shouldnothaveanybuttons");
        list.destroy();
    });

    QUnit.test('displayatooltiponafield',asyncfunction(assert){
        assert.expect(4);

        varinitialDebugMode=flectra.debug;
        flectra.debug=false;

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<tree>'+
                    '<fieldname="foo"/>'+
                    '<fieldname="bar"widget="toggle_button"/>'+
                '</tree>',
        });

        //thisisdonetoforcethetooltiptoshowimmediatelyinsteadofwaiting
        //1000ms.nottotallyacademic,butashorttestsuiteiseasiertosell:(
        list.$('th[data-name=foo]').tooltip('show',false);

        list.$('th[data-name=foo]').trigger($.Event('mouseenter'));
        assert.strictEqual($('.tooltip.oe_tooltip_string').length,0,"shouldnothaverenderedatooltip");

        flectra.debug=true;
        //itisnecessarytorerenderthelistsotooltipscanbeproperlycreated
        awaitlist.reload();
        list.$('th[data-name=foo]').tooltip('show',false);
        list.$('th[data-name=foo]').trigger($.Event('mouseenter'));
        assert.strictEqual($('.tooltip.oe_tooltip_string').length,1,"shouldhaverenderedatooltip");

        awaitlist.reload();
        list.$('th[data-name=bar]').tooltip('show',false);
        list.$('th[data-name=bar]').trigger($.Event('mouseenter'));
        assert.containsOnce($,'.oe_tooltip_technical>li[data-item="widget"]',
            'widgetshouldbepresentforthisfield');
        assert.strictEqual($('.oe_tooltip_technical>li[data-item="widget"]')[0].lastChild.wholeText.trim(),
            'Button(toggle_button)',"widgetdescriptionshouldbecorrect");

        flectra.debug=initialDebugMode;
        list.destroy();
    });

    QUnit.test('supportrowdecoration',asyncfunction(assert){
        assert.expect(2);

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<treedecoration-info="int_field>5">'+
                    '<fieldname="foo"/><fieldname="int_field"/>'+
                '</tree>',
        });

        assert.containsN(list,'tbodytr.text-info',3,
            "shouldhave3columnswithtext-infoclass");

        assert.containsN(list,'tbodytr',4,"shouldhave4rows");
        list.destroy();
    });

    QUnit.test('supportrowdecoration(withunsetnumericvalues)',asyncfunction(assert){
        assert.expect(2);

        this.data.foo.records=[];

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<treeeditable="bottom"decoration-danger="int_field&lt;0">'+
                    '<fieldname="int_field"/>'+
                '</tree>',
        });

        awaittestUtils.dom.click(list.$buttons.find('.o_list_button_add'));

        assert.containsNone(list,'tr.o_data_row.text-danger',
            "thedatarowshouldnothave.text-dangerdecoration(int_fieldisunset)");
        awaittestUtils.fields.editInput(list.$('input[name="int_field"]'),'-3');
        assert.containsOnce(list,'tr.o_data_row.text-danger',
            "thedatarowshouldhave.text-dangerdecoration(int_fieldisnegative)");
        list.destroy();
    });

    QUnit.test('supportrowdecorationwithdate',asyncfunction(assert){
        assert.expect(3);

        this.data.foo.records[0].datetime='2017-02-2712:51:35';

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<treedecoration-info="datetime==\'2017-02-2712:51:35\'"decoration-danger="datetime&gt;\'2017-02-2712:51:35\'ANDdatetime&lt;\'2017-02-2710:51:35\'">'+
                    '<fieldname="datetime"/><fieldname="int_field"/>'+
                '</tree>',
        });

        assert.containsOnce(list,'tbodytr.text-info',
            "shouldhave1columnswithtext-infoclasswithgooddatetime");

        assert.containsNone(list,'tbodytr.text-danger',
            "shouldhave0columnswithtext-dangerclasswithwrongtimezonedatetime");

        assert.containsN(list,'tbodytr',4,"shouldhave4rows");
        list.destroy();
    });

    QUnit.test('supportfielddecoration',asyncfunction(assert){
        assert.expect(3);

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:`
                <tree>
                    <fieldname="foo"decoration-danger="int_field>5"/>
                    <fieldname="int_field"/>
                </tree>`,
        });

        assert.containsN(list,'tbodytr',4,"shouldhave4rows");
        assert.containsN(list,'tbodytd.o_list_char.text-danger',3);
        assert.containsNone(list,'tbodytd.o_list_number.text-danger');

        list.destroy();
    });

    QUnit.test('bouncecreatebuttonwhennodataandclickonemptyarea',asyncfunction(assert){
        assert.expect(4);

        constlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<tree><fieldname="foo"/></tree>',
            viewOptions:{
                action:{
                    help:'<pclass="hello">clicktoaddarecord</p>'
                }
            },
        });

        assert.containsNone(list,'.o_view_nocontent');
        awaittestUtils.dom.click(list.$('.o_list_view'));
        assert.doesNotHaveClass(list.$('.o_list_button_add'),'o_catch_attention');

        awaitlist.reload({domain:[['id','<',0]]});
        assert.containsOnce(list,'.o_view_nocontent');
        awaittestUtils.dom.click(list.$('.o_view_nocontent'));
        assert.hasClass(list.$('.o_list_button_add'),'o_catch_attention');
        list.destroy();
    });

    QUnit.test('nocontenthelperwhennodata',asyncfunction(assert){
        assert.expect(5);

        varrecords=this.data.foo.records;

        this.data.foo.records=[];

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<tree><fieldname="foo"/></tree>',
            viewOptions:{
                action:{
                    help:'<pclass="hello">clicktoaddapartner</p>'
                }
            },
        });

        assert.containsOnce(list,'.o_view_nocontent',
            "shoulddisplaythenocontenthelper");

        assert.containsNone(list,'table',"shouldnothaveatableinthedom");

        assert.strictEqual(list.$('.o_view_nocontentp.hello:contains(addapartner)').length,1,
            "shouldhaverenderednocontenthelperfromaction");

        this.data.foo.records=records;
        awaitlist.reload();

        assert.containsNone(list,'.o_view_nocontent',
            "shouldnotdisplaythenocontenthelper");
        assert.containsOnce(list,'table',"shouldhaveatableinthedom");
        list.destroy();
    });

    QUnit.test('nonocontenthelperwhennodataandnohelp',asyncfunction(assert){
        assert.expect(3);

        this.data.foo.records=[];

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<tree><fieldname="foo"/></tree>',
        });

        assert.containsNone(list,'.o_view_nocontent',
            "shouldnotdisplaythenocontenthelper");

        assert.containsNone(list,'tr.o_data_row',
            "shouldnothaveanydatarow");

        assert.containsOnce(list,'table',"shouldhaveatableinthedom");
        list.destroy();
    });

    QUnit.test("emptylistwithsampledata",asyncfunction(assert){
        assert.expect(19);

        constlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:`
                <treesample="1">
                    <fieldname="foo"/>
                    <fieldname="bar"/>
                    <fieldname="int_field"/>
                    <fieldname="m2o"/>
                    <fieldname="m2m"widget="many2many_tags"/>
                    <fieldname="date"/>
                    <fieldname="datetime"/>
                </tree>`,
            domain:[['id','<',0]],//suchthatnorecordmatchesthedomain
            viewOptions:{
                action:{
                    help:'<pclass="hello">clicktoaddapartner</p>'
                }
            },
        });

        assert.hasClass(list.$el,'o_view_sample_data');
        assert.containsOnce(list,'.o_list_table');
        assert.containsN(list,'.o_data_row',10);
        assert.containsOnce(list,'.o_nocontent_help.hello');

        //Checklistsampledata
        constfirstRow=list.el.querySelector('.o_data_row');
        constcells=firstRow.querySelectorAll(':scope>.o_data_cell');
        assert.strictEqual(cells[0].innerText.trim(),"",
            "Charfieldshouldyieldanemptyelement"
        );
        assert.containsOnce(cells[1],'.custom-checkbox',
            "Booleanfieldhasbeeninstantiated"
        );
        assert.notOk(isNaN(cells[2].innerText.trim()),"Intgervalueisanumber");
        assert.ok(cells[3].innerText.trim(),"Many2onefieldisastring");

        constfirstM2MTag=cells[4].querySelector(
            ':scopespan.o_badge_text'
        ).innerText.trim();
        assert.ok(firstM2MTag.length>0,"Many2manycontainsatleastonestringtag");

        assert.ok(/\d{2}\/\d{2}\/\d{4}/.test(cells[5].innerText.trim()),
            "Datefieldshouldhavetherightformat"
        );
        assert.ok(/\d{2}\/\d{2}\/\d{4}\d{2}:\d{2}:\d{2}/.test(cells[6].innerText.trim()),
            "Datetimefieldshouldhavetherightformat"
        );

        consttextContent=list.$el.text();
        awaitlist.reload();
        assert.strictEqual(textContent,list.$el.text(),
            'Thecontentshouldbethesameafterreloadingtheviewwithoutchange'
        );

        //reloadwithanotherdomain->shouldnolongerdisplaythesamplerecords
        awaitlist.reload({domain:Domain.FALSE_DOMAIN});

        assert.doesNotHaveClass(list.$el,'o_view_sample_data');
        assert.containsNone(list,'.o_list_table');
        assert.containsOnce(list,'.o_nocontent_help.hello');

        //reloadwithanotherdomainmatchingrecords
        awaitlist.reload({domain:Domain.TRUE_DOMAIN});

        assert.doesNotHaveClass(list.$el,'o_view_sample_data');
        assert.containsOnce(list,'.o_list_table');
        assert.containsN(list,'.o_data_row',4);
        assert.containsNone(list,'.o_nocontent_help.hello');

        list.destroy();
    });

    QUnit.test("emptylistwithsampledata:toggleoptionalfield",asyncfunction(assert){
        assert.expect(9);

        constRamStorageService=AbstractStorageService.extend({
            storage:newRamStorage(),
        });

        constlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:`
                <treesample="1">
                    <fieldname="foo"/>
                    <fieldname="m2o"optional="hide"/>
                </tree>`,
            domain:Domain.FALSE_DOMAIN,
            services:{
                local_storage:RamStorageService,
            },
        });

        assert.hasClass(list.$el,'o_view_sample_data');
        assert.ok(list.$('.o_data_row').length>0);
        assert.hasClass(list.el.querySelector('.o_data_row'),'o_sample_data_disabled');
        assert.containsN(list,'th',2,"shouldhave2th,1forselectorand1forfoo");
        assert.containsOnce(list.$('table'),'.o_optional_columns_dropdown_toggle');

        awaittestUtils.dom.click(list.$('table.o_optional_columns_dropdown_toggle'));
        awaittestUtils.dom.click(list.$('div.o_optional_columnsdiv.dropdown-item:firstinput'));

        assert.hasClass(list.$el,'o_view_sample_data');
        assert.ok(list.$('.o_data_row').length>0);
        assert.hasClass(list.el.querySelector('.o_data_row'),'o_sample_data_disabled');
        assert.containsN(list,'th',3);

        list.destroy();
    });

    QUnit.test("emptylistwithsampledata:keyboardnavigation",asyncfunction(assert){
        assert.expect(11);

        constlist=awaitcreateView({
            arch:`
                <treesample="1">
                    <fieldname="foo"/>
                    <fieldname="bar"/>
                    <fieldname="int_field"/>
                </tree>`,
            data:this.data,
            domain:Domain.FALSE_DOMAIN,
            model:'foo',
            View:ListView,
        });

        //Checkkeynavisdisabled
        assert.hasClass(
            list.el.querySelector('.o_data_row'),
            'o_sample_data_disabled'
        );
        assert.hasClass(
            list.el.querySelector('.o_list_table>tfoot'),
            'o_sample_data_disabled'
        );
        assert.hasClass(
            list.el.querySelector('.o_list_table>thead.o_list_record_selector'),
            'o_sample_data_disabled'
        );
        assert.containsNone(list.renderer,'input:not([tabindex="-1"])');

        //Fromsearchbar
        assert.hasClass(document.activeElement,'o_searchview_input');

        awaittestUtils.fields.triggerKeydown(document.activeElement,'down');

        assert.hasClass(document.activeElement,'o_searchview_input');

        //From'Create'button
        document.querySelector('.btn.o_list_button_add').focus();

        assert.hasClass(document.activeElement,'o_list_button_add');

        awaittestUtils.fields.triggerKeydown(document.activeElement,'down');

        assert.hasClass(document.activeElement,'o_list_button_add');

        awaittestUtils.fields.triggerKeydown(document.activeElement,'tab');

        assert.containsNone(document.body,'.oe_tooltip_string');

        //Fromcolumnheader
        list.el.querySelector(':scopeth[data-name="foo"]').focus();

        assert.ok(document.activeElement.dataset.name==='foo');

        awaittestUtils.fields.triggerKeydown(document.activeElement,'down');

        assert.ok(document.activeElement.dataset.name==='foo');

        list.destroy();
    });

    QUnit.test('listwithgroup_by_no_leafandgroupby',asyncfunction(assert){
        assert.expect(4);

        constlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<treeexpand="1"><fieldname="foo"/></tree>',
            groupBy:['currency_id'],
            context:{group_by_no_leaf:true},
        });
        constgroups=list.el.querySelectorAll(".o_group_name");
        constgroupsRecords=[...list.el.querySelectorAll(".o_data_row.o_data_cell")];

        assert.strictEqual(groups.length,2,"Thereshouldbe2groups");
        assert.strictEqual(groups[0].textContent,"EUR(1)","Firstgroupshouldhave1record");
        assert.strictEqual(groups[1].textContent,"USD(3)","Secondgroupshouldhave3records");
        assert.deepEqual(
            groupsRecords.map(groupEl=>groupEl.textContent),
            ["yop","blip","gnap","blip"],
            "Groupsshouldcontainscorrectrecords");
        list.destroy();
    });

    QUnit.test("nonemptylistwithsampledata",asyncfunction(assert){
        assert.expect(6);

        constlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:`
                <treesample="1">
                    <fieldname="foo"/>
                    <fieldname="bar"/>
                    <fieldname="int_field"/>
                </tree>`,
            domain:Domain.TRUE_DOMAIN,
        });

        assert.containsOnce(list,'.o_list_table');
        assert.containsN(list,'.o_data_row',4);
        assert.doesNotHaveClass(list.$el,'o_view_sample_data');

        //reloadwithanotherdomainmatchingnorecord(shouldnotdisplaythesamplerecords)
        awaitlist.reload({domain:Domain.FALSE_DOMAIN});

        assert.containsOnce(list,'.o_list_table');
        assert.containsNone(list,'.o_data_row');
        assert.doesNotHaveClass(list.$el,'o_view_sample_data');

        list.destroy();
    });

    QUnit.test('clickonheaderinemptylistwithsampledata',asyncfunction(assert){
        assert.expect(4);

        constlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:`
                <treesample="1">
                    <fieldname="foo"/>
                    <fieldname="bar"/>
                    <fieldname="int_field"/>
                </tree>`,
            domain:Domain.FALSE_DOMAIN,
        });

        assert.hasClass(list,'o_view_sample_data');
        assert.containsOnce(list,'.o_list_table');
        assert.containsN(list,'.o_data_row',10);

        constcontent=list.$el.text();
        awaittestUtils.dom.click(list.$('tr:first.o_column_sortable:first'));
        assert.strictEqual(list.$el.text(),content,"thecontentshouldstillbethesame");

        list.destroy();
    });

    QUnit.test("nonemptyeditablelistwithsampledata:deleteallrecords",asyncfunction(assert){
        assert.expect(7);

        constlist=awaitcreateView({
            arch:`
                <treeeditable="top"sample="1">
                    <fieldname="foo"/>
                    <fieldname="bar"/>
                    <fieldname="int_field"/>
                </tree>`,
            data:this.data,
            domain:Domain.TRUE_DOMAIN,
            model:'foo',
            View:ListView,
            viewOptions:{
                action:{
                    help:'<pclass="hello">clicktoaddapartner</p>'
                },
                hasActionMenus:true,
            },
        });

        //Initialstate:allrecordsdisplayed
        assert.doesNotHaveClass(list,'o_view_sample_data');
        assert.containsOnce(list,'.o_list_table');
        assert.containsN(list,'.o_data_row',4);
        assert.containsNone(list,'.o_nocontent_help');

        //Deleteallrecords
        awaittestUtils.dom.click(list.el.querySelector('thead.o_list_record_selectorinput'));
        awaitcpHelpers.toggleActionMenu(list);
        awaitcpHelpers.toggleMenuItem(list,"Delete");
        awaittestUtils.dom.click($('.modal-footer.btn-primary'));

        //Finalstate:nomoresampledata,butnocontenthelperdisplayed
        assert.doesNotHaveClass(list,'o_view_sample_data');
        assert.containsNone(list,'.o_list_table');
        assert.containsOnce(list,'.o_nocontent_help');

        list.destroy();
    });

    QUnit.test("emptyeditablelistwithsampledata:startcreaterecordandcancel",asyncfunction(assert){
        assert.expect(10);

        constlist=awaitcreateView({
            arch:`
                <treeeditable="top"sample="1">
                    <fieldname="foo"/>
                    <fieldname="bar"/>
                    <fieldname="int_field"/>
                </tree>`,
            data:this.data,
            domain:Domain.FALSE_DOMAIN,
            model:'foo',
            View:ListView,
            viewOptions:{
                action:{
                    help:'<pclass="hello">clicktoaddapartner</p>'
                },
            },
        });

        //Initialstate:sampledataandnocontenthelperdisplayed
        assert.hasClass(list,'o_view_sample_data');
        assert.containsOnce(list,'.o_list_table');
        assert.containsN(list,'.o_data_row',10);
        assert.containsOnce(list,'.o_nocontent_help');

        //Startcreatingarecord
        awaittestUtils.dom.click(list.el.querySelector('.btn.o_list_button_add'));

        assert.doesNotHaveClass(list,'o_view_sample_data');
        assert.containsOnce(list,'.o_data_row');

        //Discardtemporaryrecord
        awaittestUtils.dom.click(list.el.querySelector('.btn.o_list_button_discard'));

        //Finalstate:tableshouldbedisplayedwithnodataatall
        assert.doesNotHaveClass(list,'o_view_sample_data');
        assert.containsOnce(list,'.o_list_table');
        assert.containsNone(list,'.o_data_row');
        assert.containsNone(list,'.o_nocontent_help');

        list.destroy();
    });

    QUnit.test("emptyeditablelistwithsampledata:createanddeleterecord",asyncfunction(assert){
        assert.expect(13);

        constlist=awaitcreateView({
            arch:`
                <treeeditable="top"sample="1">
                    <fieldname="foo"/>
                    <fieldname="bar"/>
                    <fieldname="int_field"/>
                </tree>`,
            data:this.data,
            domain:Domain.FALSE_DOMAIN,
            model:'foo',
            View:ListView,
            viewOptions:{
                action:{
                    help:'<pclass="hello">clicktoaddapartner</p>'
                },
                hasActionMenus:true,
            },
        });

        //Initialstate:sampledataandnocontenthelperdisplayed
        assert.hasClass(list,'o_view_sample_data');
        assert.containsOnce(list,'.o_list_table');
        assert.containsN(list,'.o_data_row',10);
        assert.containsOnce(list,'.o_nocontent_help');

        //Startcreatingarecord
        awaittestUtils.dom.click(list.el.querySelector('.btn.o_list_button_add'));

        assert.doesNotHaveClass(list,'o_view_sample_data');
        assert.containsOnce(list,'.o_data_row');

        //Savetemporaryrecord
        awaittestUtils.dom.click(list.el.querySelector('.btn.o_list_button_save'));

        assert.doesNotHaveClass(list,'o_view_sample_data');
        assert.containsOnce(list,'.o_list_table');
        assert.containsOnce(list,'.o_data_row');
        assert.containsNone(list,'.o_nocontent_help');

        //Deletenewlycreatedrecord
        awaittestUtils.dom.click(list.el.querySelector('.o_data_rowinput'));
        awaitcpHelpers.toggleActionMenu(list);
        awaitcpHelpers.toggleMenuItem(list,"Delete");
        awaittestUtils.dom.click($('.modal-footer.btn-primary'));

        //Finalstate:thereshouldbenotable,butthenocontenthelper
        assert.doesNotHaveClass(list,'o_view_sample_data');
        assert.containsNone(list,'.o_list_table');
        assert.containsOnce(list,'.o_nocontent_help');
        list.destroy();
    });

    QUnit.test('Donotdisplaynocontentwhenitisanemptyhtmltag',asyncfunction(assert){
        assert.expect(2);

        this.data.foo.records=[];

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<tree><fieldname="foo"/></tree>',
            viewOptions:{
                action:{
                    help:'<pclass="hello"></p>'
                }
            },
        });

        assert.containsNone(list,'.o_view_nocontent',
            "shouldnotdisplaythenocontenthelper");

        assert.containsOnce(list,'table',"shouldhaveatableinthedom");

        list.destroy();
    });

    QUnit.test('groupbynodewithabutton',asyncfunction(assert){
        assert.expect(14);

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<tree>'+
                '<fieldname="foo"/>'+
                '<groupbyname="currency_id">'+
                    '<buttonstring="Button1"type="object"name="button_method"/>'+
                '</groupby>'+
            '</tree>',
            mockRPC:function(route,args){
                assert.step(args.method||route);
                returnthis._super.apply(this,arguments);
            },
            intercepts:{
                execute_action:function(ev){
                    assert.deepEqual(ev.data.env.currentID,2,
                        'shouldcallwithcorrectid');
                    assert.strictEqual(ev.data.env.model,'res_currency',
                        'shouldcallwithcorrectmodel');
                    assert.strictEqual(ev.data.action_data.name,'button_method',
                        "shouldcallcorrectmethod");
                    assert.strictEqual(ev.data.action_data.type,'object',
                        'shouldhavecorrecttype');
                    ev.data.on_success();
                },
            },
        });

        assert.verifySteps(['/web/dataset/search_read']);
        assert.containsOnce(list,'theadth:not(.o_list_record_selector)',
            "thereshouldbeonlyonecolumn");

        awaitlist.update({groupBy:['currency_id']});

        assert.verifySteps(['web_read_group']);
        assert.containsN(list,'.o_group_header',2,
            "thereshouldbe2groupheaders");
        assert.containsNone(list,'.o_group_headerbutton',0,
            "thereshouldbenobuttonintheheader");

        awaittestUtils.dom.click(list.$('.o_group_header:eq(0)'));
        assert.verifySteps(['/web/dataset/search_read']);
        assert.containsOnce(list,'.o_group_headerbutton');

        awaittestUtils.dom.click(list.$('.o_group_header:eq(0)button'));

        list.destroy();
    });

    QUnit.test('groupbynodewithabuttonininnergroupbys',asyncfunction(assert){
        assert.expect(5);

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<tree>'+
                '<fieldname="foo"/>'+
                '<groupbyname="currency_id">'+
                    '<buttonstring="Button1"type="object"name="button_method"/>'+
                '</groupby>'+
            '</tree>',
            groupBy:['bar','currency_id'],
        });

        assert.containsN(list,'.o_group_header',2,
            "thereshouldbe2groupheaders");
        assert.containsNone(list,'.o_group_headerbutton',
            "thereshouldbenobuttonintheheader");

        awaittestUtils.dom.click(list.$('.o_group_header:eq(0)'));

        assert.containsN(list,'tbody:eq(1).o_group_header',2,
            "thereshouldbe2innergroupsheader");
        assert.containsNone(list,'tbody:eq(1).o_group_headerbutton',
            "thereshouldbenobuttonintheheader");

        awaittestUtils.dom.click(list.$('tbody:eq(1).o_group_header:eq(0)'));

        assert.containsOnce(list,'.o_group_headerbutton',
            "thereshouldbeonebuttonintheheader");

        list.destroy();
    });

    QUnit.test('groupbynodewithabuttonwithmodifiers',asyncfunction(assert){
        assert.expect(11);

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<tree>'+
                '<fieldname="foo"/>'+
                '<groupbyname="currency_id">'+
                    '<fieldname="position"/>'+
                    '<buttonstring="Button1"type="object"name="button_method"attrs=\'{"invisible":[("position","=","after")]}\'/>'+
                '</groupby>'+
            '</tree>',
            mockRPC:function(route,args){
                assert.step(args.method||route);
                if(args.method==='read'&&args.model==='res_currency'){
                    assert.deepEqual(args.args,[[2,1],['position']]);
                }
                returnthis._super.apply(this,arguments);
            },
            groupBy:['currency_id'],
        });

        assert.verifySteps(['web_read_group','read']);

        awaittestUtils.dom.click(list.$('.o_group_header:eq(0)'));

        assert.verifySteps(['/web/dataset/search_read']);
        assert.containsOnce(list,'.o_group_headerbutton.o_invisible_modifier',
            "thefirstgroup(EUR)shouldhaveaninvisiblebutton");

        awaittestUtils.dom.click(list.$('.o_group_header:eq(1)'));

        assert.verifySteps(['/web/dataset/search_read']);
        assert.containsN(list,'.o_group_headerbutton',2,
            "thereshouldbetwobuttons(onebyheader)");
        assert.doesNotHaveClass(list,'.o_group_header:eq(1)button','o_invisible_modifier',
            "thesecondheaderbuttonshouldbevisible");

        list.destroy();
    });

    QUnit.test('groupbynodewithabuttonwithmodifiersusingamany2one',asyncfunction(assert){
        assert.expect(5);

        this.data.res_currency.fields.m2o={string:"CurrencyM2O",type:"many2one",relation:"bar"};
        this.data.res_currency.records[0].m2o=1;

        constlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:`
                <treeexpand="1">
                    <fieldname="foo"/>
                    <groupbyname="currency_id">
                        <fieldname="m2o"/>
                        <buttonstring="Button1"type="object"name="button_method"attrs='{"invisible":[("m2o","=",false)]}'/>
                    </groupby>
                </tree>`,
            mockRPC(route,args){
                assert.step(args.method);
                returnthis._super(...arguments);
            },
            groupBy:['currency_id'],
        });

        assert.containsOnce(list,'.o_group_header:eq(0)button.o_invisible_modifier');
        assert.containsOnce(list,'.o_group_header:eq(1)button:not(.o_invisible_modifier)');

        assert.verifySteps(['web_read_group','read']);

        list.destroy();
    });

    QUnit.test('reloadlistviewwithgroupbynode',asyncfunction(assert){
        assert.expect(2);

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<treeexpand="1">'+
                '<fieldname="foo"/>'+
                '<groupbyname="currency_id">'+
                    '<fieldname="position"/>'+
                    '<buttonstring="Button1"type="object"name="button_method"attrs=\'{"invisible":[("position","=","after")]}\'/>'+
                '</groupby>'+
            '</tree>',
            groupBy:['currency_id'],
        });

        assert.containsOnce(list,'.o_group_headerbutton:not(.o_invisible_modifier)',
            "thereshouldbeonevisiblebutton");

        awaitlist.reload({domain:[]});
        assert.containsOnce(list,'.o_group_headerbutton:not(.o_invisible_modifier)',
            "thereshouldstillbeonevisiblebutton");

        list.destroy();
    });

    QUnit.test('editablelistviewwithgroupbynodeandmodifiers',asyncfunction(assert){
        assert.expect(3);

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<treeexpand="1"editable="bottom">'+
                '<fieldname="foo"/>'+
                '<groupbyname="currency_id">'+
                    '<fieldname="position"/>'+
                    '<buttonstring="Button1"type="object"name="button_method"attrs=\'{"invisible":[("position","=","after")]}\'/>'+
                '</groupby>'+
            '</tree>',
            groupBy:['currency_id'],
        });

        assert.doesNotHaveClass(list.$('.o_data_row:first'),'o_selected_row',
            "firstrowshouldbeinreadonlymode");

        awaittestUtils.dom.click(list.$('.o_data_row:first.o_data_cell'));
        assert.hasClass(list.$('.o_data_row:first'),'o_selected_row',
            "therowshouldbeineditmode");

        awaittestUtils.fields.triggerKeydown($(document.activeElement),'escape');
        assert.doesNotHaveClass(list.$('.o_data_row:first'),'o_selected_row',
            "therowshouldbebackinreadonlymode");

        list.destroy();
    });

    QUnit.test('groupbynodewitheditbutton',asyncfunction(assert){
        assert.expect(1);

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<treeexpand="1">'+
                '<fieldname="foo"/>'+
                '<groupbyname="currency_id">'+
                    '<buttonstring="Button1"type="edit"name="edit"/>'+
                '</groupby>'+
            '</tree>',
            groupBy:['currency_id'],
            intercepts:{
                do_action:function(event){
                    assert.deepEqual(event.data.action,{
                        context:{create:false},
                        res_id:2,
                        res_model:'res_currency',
                        type:'ir.actions.act_window',
                        views:[[false,'form']],
                        flags:{mode:'edit'},
                    },"shouldtriggerdo_actionwithcorrectactionparameter");
                }
            },
        });
        awaittestUtils.dom.click(list.$('.o_group_header:eq(0)button'));
        list.destroy();
    });

    QUnit.test('groupbynodewithsubfields,andonchange',asyncfunction(assert){
        assert.expect(1);

        this.data.foo.onchanges={
            foo:function(){},
        };

        constlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:`<treeeditable="bottom"expand="1">
                    <fieldname="foo"/>
                    <fieldname="currency_id"/>
                    <groupbyname="currency_id">
                        <fieldname="position"invisible="1"/>
                    </groupby>
                </tree>`,
            groupBy:['currency_id'],
            mockRPC:function(route,args){
                if(args.method==='onchange'){
                    assert.deepEqual(args.args[3],{
                        foo:"1",
                        currency_id:"",
                    },'onchangespecshouldnotfollowrelationofmany2onefields');
                }
                returnthis._super.apply(this,arguments);
            },
        });

        awaittestUtils.dom.click(list.$('.o_data_row:first.o_data_cell:first'));
        awaittestUtils.fields.editInput(list.$('.o_field_widget[name=foo]'),"newvalue");

        list.destroy();
    });

    QUnit.test('listview,editable,withoutdata',asyncfunction(assert){
        assert.expect(12);

        this.data.foo.records=[];

        this.data.foo.fields.date.default="2017-02-10";

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<treestring="Phonecalls"editable="top">'+
                    '<fieldname="date"/>'+
                    '<fieldname="m2o"/>'+
                    '<fieldname="foo"/>'+
                    '<buttontype="object"icon="fa-plus-square"name="method"/>'+
                '</tree>',
            viewOptions:{
                action:{
                    help:'<pclass="hello">clicktoaddapartner</p>'
                }
            },
            mockRPC:function(route,args){
                if(args.method==='create'){
                    assert.ok(true,"shouldhavecreatedarecord");
                }
                returnthis._super.apply(this,arguments);
            },
        });

        assert.containsOnce(list,'.o_view_nocontent',
            "shouldhaveanocontenthelperdisplayed");

        assert.containsNone(list,'div.table-responsive',
            "shouldnothaveadiv.table-responsive");
        assert.containsNone(list,'table',"shouldnothaverenderedatable");

        awaittestUtils.dom.click(list.$buttons.find('.o_list_button_add'));

        assert.containsNone(list,'.o_view_nocontent',
            "shouldnothaveanocontenthelperdisplayed");
        assert.containsOnce(list,'table',"shouldhaverenderedatable");

        assert.hasClass(list.$('tbodytr:eq(0)'),'o_selected_row',
            "thedatefieldtdshouldbeineditmode");
        assert.strictEqual(list.$('tbodytr:eq(0)td:eq(1)').text().trim(),"",
            "thedatefieldtdshouldnothaveanycontent");

        assert.strictEqual(list.$('tr.o_selected_row.o_list_record_selectorinput').prop('disabled'),true,
            "recordselectorcheckboxshouldbedisabledwhiletherecordisnotyetcreated");
        assert.strictEqual(list.$('.o_list_buttonbutton').prop('disabled'),true,
            "buttonsshouldbedisabledwhiletherecordisnotyetcreated");

        awaittestUtils.dom.click(list.$buttons.find('.o_list_button_save'));

        assert.strictEqual(list.$('tbodytr:eq(0).o_list_record_selectorinput').prop('disabled'),false,
            "recordselectorcheckboxshouldnotbedisabledoncetherecordiscreated");
        assert.strictEqual(list.$('.o_list_buttonbutton').prop('disabled'),false,
            "buttonsshouldnotbedisabledoncetherecordiscreated");

        list.destroy();
    });

    QUnit.test('listview,editable,withabutton',asyncfunction(assert){
        assert.expect(1);

        this.data.foo.records=[];

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<treestring="Phonecalls"editable="top">'+
                    '<fieldname="foo"/>'+
                    '<buttonstring="abc"icon="fa-phone"type="object"name="schedule_another_phonecall"/>'+
                '</tree>',
        });

        awaittestUtils.dom.click(list.$buttons.find('.o_list_button_add'));

        assert.containsOnce(list,'tablebutton.o_icon_buttoni.fa-phone',
            "shouldhaverenderedabutton");
        list.destroy();
    });

    QUnit.test('listviewwithabuttonwithouticon',asyncfunction(assert){
        assert.expect(1);

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<treestring="Phonecalls"editable="top">'+
                    '<fieldname="foo"/>'+
                    '<buttonstring="abc"type="object"name="schedule_another_phonecall"/>'+
                '</tree>',
        });

        assert.strictEqual(list.$('tablebutton').first().text(),'abc',
            "shouldhaverenderedabuttonwithstringattributeaslabel");
        list.destroy();
    });

    QUnit.test('listview,editable,candiscard',asyncfunction(assert){
        assert.expect(5);

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<treestring="Phonecalls"editable="top">'+
                    '<fieldname="foo"/>'+
                '</tree>',
        });

        assert.strictEqual(list.$('td:not(.o_list_record_selector)input').length,0,"noinputshouldbeinthetable");

        awaittestUtils.dom.click(list.$('tbodytd:not(.o_list_record_selector):first'));
        assert.strictEqual(list.$('td:not(.o_list_record_selector)input').length,1,"firstcellshouldbeeditable");

        assert.ok(list.$buttons.find('.o_list_button_discard').is(':visible'),
            "discardbuttonshouldbevisible");

        awaittestUtils.dom.click(list.$buttons.find('.o_list_button_discard'));

        assert.strictEqual(list.$('td:not(.o_list_record_selector)input').length,0,"noinputshouldbeinthetable");

        assert.ok(!list.$buttons.find('.o_list_button_discard').is(':visible'),
            "discardbuttonshouldnotbevisible");
        list.destroy();
    });

    QUnit.test('editablelistview,clickonthelisttosave',asyncfunction(assert){
        assert.expect(3);

        this.data.foo.fields.date.default="2017-02-10";
        this.data.foo.records=[];

        varcreateCount=0;

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<treestring="Phonecalls"editable="top">'+
                    '<fieldname="date"/>'+
                '</tree>',
            mockRPC:function(route,args){
                if(args.method==='create'){
                    createCount++;
                }
                returnthis._super.apply(this,arguments);
            },
        });

        awaittestUtils.dom.click(list.$buttons.find('.o_list_button_add'));
        awaittestUtils.dom.click(list.$('.o_list_view'));

        assert.strictEqual(createCount,1,"shouldhavecreatedarecord");

        awaittestUtils.dom.click(list.$buttons.find('.o_list_button_add'));
        awaittestUtils.dom.click(list.$('tfoot'));

        assert.strictEqual(createCount,2,"shouldhavecreatedarecord");

        awaittestUtils.dom.click(list.$buttons.find('.o_list_button_add'));
        awaittestUtils.dom.click(list.$('tbodytr').last());

        assert.strictEqual(createCount,3,"shouldhavecreatedarecord");
        list.destroy();
    });

    QUnit.test('clickonabuttoninalistview',asyncfunction(assert){
        assert.expect(9);

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<tree>'+
                    '<fieldname="foo"/>'+
                    '<buttonstring="abutton"name="button_action"icon="fa-car"type="object"/>'+
                '</tree>',
            mockRPC:function(route){
                assert.step(route);
                returnthis._super.apply(this,arguments);
            },
            intercepts:{
                execute_action:function(event){
                    assert.deepEqual(event.data.env.currentID,1,
                        'shouldcallwithcorrectid');
                    assert.strictEqual(event.data.env.model,'foo',
                        'shouldcallwithcorrectmodel');
                    assert.strictEqual(event.data.action_data.name,'button_action',
                        "shouldcallcorrectmethod");
                    assert.strictEqual(event.data.action_data.type,'object',
                        'shouldhavecorrecttype');
                    event.data.on_closed();
                },
            },
        });

        assert.containsN(list,'tbody.o_list_button',4,
            "thereshouldbeonebuttonperrow");
        assert.containsOnce(list,'tbody.o_list_button:first.o_icon_button.fa.fa-car',
            'buttonsshouldhavecorrecticon');

        awaittestUtils.dom.click(list.$('tbody.o_list_button:first>button'));
        assert.verifySteps(['/web/dataset/search_read','/web/dataset/search_read'],
            "shouldhavereloadedtheview(aftertheactioniscomplete)");
        list.destroy();
    });

    QUnit.test('invisibleattrsinreadonlyandeditablelist',asyncfunction(assert){
        assert.expect(5);

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<treeeditable="top">'+
                    '<buttonstring="abutton"name="button_action"icon="fa-car"'+
                        'type="object"attrs="{\'invisible\':[(\'id\',\'=\',1)]}"/>'+
                    '<fieldname="int_field"/>'+
                    '<fieldname="qux"/>'+
                    '<fieldname="foo"attrs="{\'invisible\':[(\'id\',\'=\',1)]}"/>'+
                '</tree>',
        });

        assert.equal(list.$('tbodytr:nth(0)td:nth(4)').html(),"",
            "tdthatcontainsaninvisiblefieldshouldbeempty");
        assert.hasClass(list.$('tbodytr:nth(0)td:nth(1)button'),"o_invisible_modifier",
            "buttonwithinvisibleattrsshouldbeproperlyhidden");

        //editfirstrow
        awaittestUtils.dom.click(list.$('tbodytr:nth(0)td:nth(2)'));
        assert.strictEqual(list.$('tbodytr:nth(0)td:nth(4)input.o_invisible_modifier').length,1,
            "tdthatcontainsaninvisiblefieldshouldnotbeemptyinedition");
        assert.hasClass(list.$('tbodytr:nth(0)td:nth(1)button'),"o_invisible_modifier",
            "buttonwithinvisibleattrsshouldbeproperlyhidden");
        awaittestUtils.dom.click(list.$buttons.find('.o_list_button_discard'));

        //clickontheinvisiblefield'scelltoeditfirstrow
        awaittestUtils.dom.click(list.$('tbodytr:nth(0)td:nth(4)'));
        assert.hasClass(list.$('tbodytr:nth(0)'),'o_selected_row',
            "firstrowshouldbeinedition");
        list.destroy();
    });

    QUnit.test('monetaryfieldsareproperlyrendered',asyncfunction(assert){
        assert.expect(3);

        varcurrencies={};
        _.each(this.data.res_currency.records,function(currency){
            currencies[currency.id]=currency;
        });
        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<tree>'+
                    '<fieldname="id"/>'+
                    '<fieldname="amount"/>'+
                    '<fieldname="currency_id"invisible="1"/>'+
                '</tree>',
            session:{
                currencies:currencies,
            },
        });

        assert.containsN(list,'tbodytr:firsttd',3,
            "currency_idcolumnshouldnotbeinthetable");
        assert.strictEqual(list.$('tbodytr:firsttd:nth(2)').text().replace(/\s/g,''),
            '1200.00€',"currency_idcolumnshouldnotbeinthetable");
        assert.strictEqual(list.$('tbodytr:nth(1)td:nth(2)').text().replace(/\s/g,''),
            '$500.00',"currency_idcolumnshouldnotbeinthetable");

        list.destroy();
    });

    QUnit.test('simplelistwithdateanddatetime',asyncfunction(assert){
        assert.expect(2);

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<tree><fieldname="date"/><fieldname="datetime"/></tree>',
            session:{
                getTZOffset:function(){
                    return120;
                },
            },
        });

        assert.strictEqual(list.$('td:eq(1)').text(),"01/25/2017",
            "shouldhaveformattedthedate");
        assert.strictEqual(list.$('td:eq(2)').text(),"12/12/201612:55:05",
            "shouldhaveformattedthedatetime");
        list.destroy();
    });

    QUnit.test('editarowbyclickingonareadonlyfield',asyncfunction(assert){
        assert.expect(9);

        this.data.foo.fields.foo.readonly=true;

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<treeeditable="bottom"><fieldname="foo"/><fieldname="int_field"/></tree>',
        });

        assert.hasClass(list.$('.o_data_row:firsttd:nth(1)'),'o_readonly_modifier',
            "foofieldcellsshouldhaveclass'o_readonly_modifier'");

        //editthefirstrow
        awaittestUtils.dom.click(list.$('.o_data_row:firsttd:nth(1)'));
        assert.hasClass(list.$('.o_data_row:first'),'o_selected_row',
            "firstrowshouldbeselected");
        var$cell=list.$('.o_data_row:firsttd:nth(1)');
        //review
        assert.hasClass($cell,'o_readonly_modifier');
        assert.hasClass($cell.parent(),'o_selected_row');
        assert.strictEqual(list.$('.o_data_row:firsttd:nth(1)span').text(),'yop',
            "awidgetshouldhavebeenrenderedforreadonlyfields");
        assert.hasClass(list.$('.o_data_row:firsttd:nth(2)').parent(),'o_selected_row',
            "field'int_field'shouldbeinedition");
        assert.strictEqual(list.$('.o_data_row:firsttd:nth(2)input').length,1,
            "awidgetforfield'int_fieldshouldhavebeenrendered'");

        //clickagainonreadonlycelloffirstline:nothingshouldhavechanged
        awaittestUtils.dom.click(list.$('.o_data_row:firsttd:nth(1)'));
        assert.hasClass(list.$('.o_data_row:first'),'o_selected_row',
            "firstrowshouldbeselected");
        assert.strictEqual(list.$('.o_data_row:firsttd:nth(2)input').length,1,
            "awidgetforfield'int_field'shouldhavebeenrendered(onlyonce)");

        list.destroy();
    });

    QUnit.test('listviewwithnestedgroups',asyncfunction(assert){
        assert.expect(42);

        this.data.foo.records.push({id:5,foo:"blip",int_field:-7,m2o:1});
        this.data.foo.records.push({id:6,foo:"blip",int_field:5,m2o:2});

        varnbRPCs={readGroup:0,searchRead:0};
        varenvIDs=[];//theidsthatshouldbeintheenvironmentduringthistest

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<tree><fieldname="id"/><fieldname="int_field"/></tree>',
            groupBy:['m2o','foo'],
            mockRPC:function(route,args){
                if(args.method==='web_read_group'){
                    if(args.kwargs.groupby[0]==='foo'){//nestedread_group
                        //calledtwice(oncewhenopeningthegroup,oncewhensorting)
                        assert.deepEqual(args.kwargs.domain,[['m2o','=',1]],
                            "nestedread_groupshouldbecalledwithcorrectdomain");
                    }
                    nbRPCs.readGroup++;
                }elseif(route==='/web/dataset/search_read'){
                    //calledtwice(oncewhenopeningthegroup,oncewhensorting)
                    assert.deepEqual(args.domain,[['foo','=','blip'],['m2o','=',1]],
                        "nestedsearch_readshouldbecalledwithcorrectdomain");
                    nbRPCs.searchRead++;
                }
                returnthis._super.apply(this,arguments);
            },
            intercepts:{
                switch_view:function(event){
                    assert.strictEqual(event.data.res_id,4,
                        "'switch_view'eventhasbeentriggered");
                },
            },
        });

        assert.strictEqual(nbRPCs.readGroup,1,"shouldhavedoneoneread_group");
        assert.strictEqual(nbRPCs.searchRead,0,"shouldhavedonenosearch_read");
        assert.deepEqual(list.exportState().resIds,envIDs);

        //basicrenderingtests
        assert.containsOnce(list,'tbody',"thereshouldbe1tbody");
        assert.containsN(list,'.o_group_header',2,
            "shouldcontain2groupsatfirstlevel");
        assert.strictEqual(list.$('.o_group_name:first').text(),'Value1(4)',
            "groupshouldhavecorrectnameandcount");
        assert.containsN(list,'.o_group_name.fa-caret-right',2,
            "thecarretofclosedgroupsshouldberight");
        assert.strictEqual(list.$('.o_group_name:firstspan').css('padding-left'),
            '2px',"groupsoflevel1shouldhavea2pxpadding-left");
        assert.strictEqual(list.$('.o_group_header:firsttd:last').text(),'16',
            "groupaggregatesarecorrectlydisplayed");

        //openthefirstgroup
        nbRPCs={readGroup:0,searchRead:0};
        awaittestUtils.dom.click(list.$('.o_group_header:first'));
        assert.strictEqual(nbRPCs.readGroup,1,"shouldhavedoneoneread_group");
        assert.strictEqual(nbRPCs.searchRead,0,"shouldhavedonenosearch_read");
        assert.deepEqual(list.exportState().resIds,envIDs);

        var$openGroup=list.$('tbody:nth(1)');
        assert.strictEqual(list.$('.o_group_name:first').text(),'Value1(4)',
            "groupshouldhavecorrectnameandcount(ofrecords,notinnersubgroups)");
        assert.containsN(list,'tbody',3,"thereshouldbe3tbodys");
        assert.containsOnce(list,'.o_group_name:first.fa-caret-down',
            "thecarretofopengroupsshouldbedown");
        assert.strictEqual($openGroup.find('.o_group_header').length,3,
            "opengroupshouldcontain3groups");
        assert.strictEqual($openGroup.find('.o_group_name:nth(2)').text(),'blip(2)',
            "groupshouldhavecorrectnameandcount");
        assert.strictEqual($openGroup.find('.o_group_name:nth(2)span').css('padding-left'),
            '22px',"groupsoflevel2shouldhavea22pxpadding-left");
        assert.strictEqual($openGroup.find('.o_group_header:nth(2)td:last').text(),'-11',
            "innergroupaggregatesarecorrectlydisplayed");

        //opensubgroup
        nbRPCs={readGroup:0,searchRead:0};
        envIDs=[4,5];//theopenedsubgroupcontainsthesetworecords
        awaittestUtils.dom.click($openGroup.find('.o_group_header:nth(2)'));
        assert.strictEqual(nbRPCs.readGroup,0,"shouldhavedonenoread_group");
        assert.strictEqual(nbRPCs.searchRead,1,"shouldhavedoneonesearch_read");
        assert.deepEqual(list.exportState().resIds,envIDs);

        var$openSubGroup=list.$('tbody:nth(2)');
        assert.containsN(list,'tbody',4,"thereshouldbe4tbodys");
        assert.strictEqual($openSubGroup.find('.o_data_row').length,2,
            "opensubgroupshouldcontain2datarows");
        assert.strictEqual($openSubGroup.find('.o_data_row:firsttd:last').text(),'-4',
            "firstrecordinopensubgroupshouldberes_id4(withint_field-4)");

        //openarecord(shouldtriggerevent'open_record')
        awaittestUtils.dom.click($openSubGroup.find('.o_data_row:first'));

        //sortbyint_field(ASC)andcheckthatopengroupsarestillopen
        nbRPCs={readGroup:0,searchRead:0};
        envIDs=[5,4];//orderoftherecordschanged
        awaittestUtils.dom.click(list.$('theadth:last'));
        assert.strictEqual(nbRPCs.readGroup,2,"shouldhavedonetworead_groups");
        assert.strictEqual(nbRPCs.searchRead,1,"shouldhavedoneonesearch_read");
        assert.deepEqual(list.exportState().resIds,envIDs);

        $openSubGroup=list.$('tbody:nth(2)');
        assert.containsN(list,'tbody',4,"thereshouldbe4tbodys");
        assert.strictEqual($openSubGroup.find('.o_data_row').length,2,
            "opensubgroupshouldcontain2datarows");
        assert.strictEqual($openSubGroup.find('.o_data_row:firsttd:last').text(),'-7',
            "firstrecordinopensubgroupshouldberes_id5(withint_field-7)");

        //closefirstlevelgroup
        nbRPCs={readGroup:0,searchRead:0};
        envIDs=[];//thegroupbeingclosed,thereisnomorerecordintheenvironment
        awaittestUtils.dom.click(list.$('.o_group_header:nth(1)'));
        assert.strictEqual(nbRPCs.readGroup,0,"shouldhavedonenoread_group");
        assert.strictEqual(nbRPCs.searchRead,0,"shouldhavedonenosearch_read");
        assert.deepEqual(list.exportState().resIds,envIDs);

        assert.containsOnce(list,'tbody',"thereshouldbe1tbody");
        assert.containsN(list,'.o_group_header',2,
            "shouldcontain2groupsatfirstlevel");
        assert.containsN(list,'.o_group_name.fa-caret-right',2,
            "thecarretofclosedgroupsshouldberight");

        list.destroy();
    });

    QUnit.test('groupedlistonselectionfieldatlevel2',asyncfunction(assert){
        assert.expect(4);

        this.data.foo.fields.priority={
            string:"Priority",
            type:"selection",
            selection:[[1,"Low"],[2,"Medium"],[3,"High"]],
            default:1,
        };
        this.data.foo.records.push({id:5,foo:"blip",int_field:-7,m2o:1,priority:2});
        this.data.foo.records.push({id:6,foo:"blip",int_field:5,m2o:1,priority:3});

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<tree><fieldname="id"/><fieldname="int_field"/></tree>',
            groupBy:['m2o','priority'],
        });

        assert.containsN(list,'.o_group_header',2,
            "shouldcontain2groupsatfirstlevel");

        //openthefirstgroup
        awaittestUtils.dom.click(list.$('.o_group_header:first'));

        var$openGroup=list.$('tbody:nth(1)');
        assert.strictEqual($openGroup.find('tr').length,3,
            "shouldhave3subgroups");
        assert.strictEqual($openGroup.find('tr').length,3,
            "shouldhave3subgroups");
        assert.strictEqual($openGroup.find('.o_group_name:first').text(),'Low(3)',
            "shoulddisplaytheselectionnameinthegroupheader");

        list.destroy();
    });

    QUnit.test('groupedlistwithapagerinagroup',asyncfunction(assert){
        assert.expect(6);
        this.data.foo.records[3].bar=true;

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<tree><fieldname="foo"/><fieldname="bar"/></tree>',
            groupBy:['bar'],
            viewOptions:{
                limit:3,
            },
        });
        varheaderHeight=list.$('.o_group_header').css('height');

        //basicrenderingchecks
        awaittestUtils.dom.click(list.$('.o_group_header'));
        assert.strictEqual(list.$('.o_group_header').css('height'),headerHeight,
            "heightofgroupheadershouldn'thavechanged");
        assert.hasClass(list.$('.o_group_headerth:eq(1)>nav'),'o_pager',
            "lastcellofopengroupheadershouldhaveclassname'o_pager'");

        assert.strictEqual(cpHelpers.getPagerValue('.o_group_header'),'1-3',
            "pager'svalueshouldbecorrect");
        assert.containsN(list,'.o_data_row',3,
            "opengroupshoulddisplay3records");

        //gotonextpage
        awaitcpHelpers.pagerNext('.o_group_header');
        assert.strictEqual(cpHelpers.getPagerValue('.o_group_header'),'4-4',
            "pager'svalueshouldbecorrect");
        assert.containsOnce(list,'.o_data_row',
            "opengroupshoulddisplay1record");

        list.destroy();
    });

    QUnit.test('edition:createnewline,thendiscard',asyncfunction(assert){
        assert.expect(11);

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<treeeditable="bottom"><fieldname="foo"/><fieldname="bar"/></tree>',
        });

        assert.containsN(list,'tr.o_data_row',4,
            "shouldhave4records");
        assert.strictEqual(list.$buttons.find('.o_list_button_add:visible').length,1,
            "createbuttonshouldbevisible");
        assert.strictEqual(list.$buttons.find('.o_list_button_discard:visible').length,0,
            "discardbuttonshouldbehidden");
        assert.containsN(list,'.o_list_record_selectorinput:enabled',5);
        awaittestUtils.dom.click(list.$buttons.find('.o_list_button_add'));
        assert.strictEqual(list.$buttons.find('.o_list_button_add:visible').length,0,
            "createbuttonshouldbehidden");
        assert.strictEqual(list.$buttons.find('.o_list_button_discard:visible').length,1,
            "discardbuttonshouldbevisible");
        assert.containsNone(list,'.o_list_record_selectorinput:enabled');
        awaittestUtils.dom.click(list.$buttons.find('.o_list_button_discard'));
        assert.containsN(list,'tr.o_data_row',4,
            "shouldstillhave4records");
        assert.strictEqual(list.$buttons.find('.o_list_button_add:visible').length,1,
            "createbuttonshouldbevisibleagain");
        assert.strictEqual(list.$buttons.find('.o_list_button_discard:visible').length,0,
            "discardbuttonshouldbehiddenagain");
        assert.containsN(list,'.o_list_record_selectorinput:enabled',5);

        list.destroy();
    });

    QUnit.test('invisibleattrsonfieldsarere-evaluatedonfieldchange',asyncfunction(assert){
        assert.expect(7);

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:
                '<treeeditable="top">'+
                    '<fieldname="foo"attrs="{\'invisible\':[[\'bar\',\'=\',True]]}"/>'+
                    '<fieldname="bar"/>'+
                '</tree>',
        });

        assert.containsN(list,'tbodytd.o_invisible_modifier',3,
            "thereshouldbe3invisiblefoocellsinreadonlymode");

        //Makefirstlineeditable
        awaittestUtils.dom.click(list.$('tbodytr:nth(0)td:nth(1)'));

        assert.strictEqual(list.$('tbodytr:nth(0)td:nth(1)>input[name="foo"].o_invisible_modifier').length,1,
            "thefoofieldwidgetshouldhavebeenrenderedasinvisible");

        awaittestUtils.dom.click(list.$('tbodytr:nth(0)td:nth(2)input'));
        assert.strictEqual(list.$('tbodytr:nth(0)td:nth(1)>input[name="foo"]:not(.o_invisible_modifier)').length,1,
            "thefoofieldwidgetshouldhavebeenmarkedasnon-invisible");
        assert.containsN(list,'tbodytd.o_invisible_modifier',2,
            "thefoofieldwidgetparentcellshouldnotbeinvisibleanymore");

        awaittestUtils.dom.click(list.$('tbodytr:nth(0)td:nth(2)input'));
        assert.strictEqual(list.$('tbodytr:nth(0)td:nth(1)>input[name="foo"].o_invisible_modifier').length,1,
            "thefoofieldwidgetshouldhavebeenmarkedasinvisibleagain");
        assert.containsN(list,'tbodytd.o_invisible_modifier',3,
            "thefoofieldwidgetparentcellshouldnowbeinvisibleagain");

        //Reswitchthecelltoeditableandsavetherow
        awaittestUtils.dom.click(list.$('tbodytr:nth(0)td:nth(2)input'));
        awaittestUtils.dom.click(list.$('thead'));

        assert.containsN(list,'tbodytd.o_invisible_modifier',2,
            "thereshouldbe2invisiblefoocellsinreadonlymode");

        list.destroy();
    });

    QUnit.test('readonlyattrsonfieldsarere-evaluatedonfieldchange',asyncfunction(assert){
        assert.expect(9);

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:
                '<treeeditable="top">'+
                    '<fieldname="foo"attrs="{\'readonly\':[[\'bar\',\'=\',True]]}"/>'+
                    '<fieldname="bar"/>'+
                '</tree>',
        });

        assert.containsN(list,'tbodytd.o_readonly_modifier',3,
            "thereshouldbe3readonlyfoocellsinreadonlymode");

        //Makefirstlineeditable
        awaittestUtils.dom.click(list.$('tbodytr:nth(0)td:nth(1)'));

        assert.strictEqual(list.$('tbodytr:nth(0)td:nth(1)>span[name="foo"]').length,1,
            "thefoofieldwidgetshouldhavebeenrenderedasreadonly");

        awaittestUtils.dom.click(list.$('tbodytr:nth(0)td:nth(2)input'));
        assert.strictEqual(list.$('tbodytr:nth(0)td:nth(1)>input[name="foo"]').length,1,
            "thefoofieldwidgetshouldhavebeenrerenderedaseditable");
        assert.containsN(list,'tbodytd.o_readonly_modifier',2,
            "thefoofieldwidgetparentcellshouldnotbereadonlyanymore");

        awaittestUtils.dom.click(list.$('tbodytr:nth(0)td:nth(2)input'));
        assert.strictEqual(list.$('tbodytr:nth(0)td:nth(1)>span[name="foo"]').length,1,
            "thefoofieldwidgetshouldhavebeenrerenderedasreadonly");
        assert.containsN(list,'tbodytd.o_readonly_modifier',3,
            "thefoofieldwidgetparentcellshouldnowbereadonlyagain");

        awaittestUtils.dom.click(list.$('tbodytr:nth(0)td:nth(2)input'));
        assert.strictEqual(list.$('tbodytr:nth(0)td:nth(1)>input[name="foo"]').length,1,
            "thefoofieldwidgetshouldhavebeenrerenderedaseditableagain");
        assert.containsN(list,'tbodytd.o_readonly_modifier',2,
            "thefoofieldwidgetparentcellshouldnotbereadonlyagain");

        //Clickoutsidetoleaveeditionmode
        awaittestUtils.dom.click(list.$el);

        assert.containsN(list,'tbodytd.o_readonly_modifier',2,
            "thereshouldbe2readonlyfoocellsinreadonlymode");

        list.destroy();
    });

    QUnit.test('requiredattrsonfieldsarere-evaluatedonfieldchange',asyncfunction(assert){
        assert.expect(7);

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:
                '<treeeditable="top">'+
                    '<fieldname="foo"attrs="{\'required\':[[\'bar\',\'=\',True]]}"/>'+
                    '<fieldname="bar"/>'+
                '</tree>',
        });

        assert.containsN(list,'tbodytd.o_required_modifier',3,
            "thereshouldbe3requiredfoocellsinreadonlymode");

        //Makefirstlineeditable
        awaittestUtils.dom.click(list.$('tbodytr:nth(0)td:nth(1)'));

        assert.strictEqual(list.$('tbodytr:nth(0)td:nth(1)>input[name="foo"].o_required_modifier').length,1,
            "thefoofieldwidgetshouldhavebeenrenderedasrequired");

        awaittestUtils.dom.click(list.$('tbodytr:nth(0)td:nth(2)input'));
        assert.strictEqual(list.$('tbodytr:nth(0)td:nth(1)>input[name="foo"]:not(.o_required_modifier)').length,1,
            "thefoofieldwidgetshouldhavebeenmarkedasnon-required");
        assert.containsN(list,'tbodytd.o_required_modifier',2,
            "thefoofieldwidgetparentcellshouldnotberequiredanymore");

        awaittestUtils.dom.click(list.$('tbodytr:nth(0)td:nth(2)input'));
        assert.strictEqual(list.$('tbodytr:nth(0)td:nth(1)>input[name="foo"].o_required_modifier').length,1,
            "thefoofieldwidgetshouldhavebeenmarkedasrequiredagain");
        assert.containsN(list,'tbodytd.o_required_modifier',3,
            "thefoofieldwidgetparentcellshouldnowberequiredagain");

        //Reswitchthecelltoeditableandsavetherow
        awaittestUtils.dom.click(list.$('tbodytr:nth(0)td:nth(2)input'));
        awaittestUtils.dom.click(list.$('thead'));

        assert.containsN(list,'tbodytd.o_required_modifier',2,
            "thereshouldbe2requiredfoocellsinreadonlymode");

        list.destroy();
    });

    QUnit.test('leavingunvalidrowsinedition',asyncfunction(assert){
        assert.expect(4);

        varwarnings=0;
        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:
                '<treeeditable="bottom">'+
                    '<fieldname="foo"required="1"/>'+
                    '<fieldname="bar"/>'+
                '</tree>',
            services:{
                notification:NotificationService.extend({
                    notify:function(params){
                        if(params.type==='danger'){
                            warnings++;
                        }
                    }
                }),
            },
        });

        //Startfirstlineedition
        var$firstFooTd=list.$('tbodytr:nth(0)td:nth(1)');
        awaittestUtils.dom.click($firstFooTd);

        //Removerequiredfoofieldvalue
        awaittestUtils.fields.editInput($firstFooTd.find('input'),"");

        //Trystartingotherlineedition
        var$secondFooTd=list.$('tbodytr:nth(1)td:nth(1)');
        awaittestUtils.dom.click($secondFooTd);
        awaittestUtils.nextTick();

        assert.strictEqual($firstFooTd.parent('.o_selected_row').length,1,
            "firstlineshouldstillbeineditionasinvalid");
        assert.containsOnce(list,'tbodytr.o_selected_row',
            "nootherlineshouldbeinedition");
        assert.strictEqual($firstFooTd.find('input.o_field_invalid').length,1,
            "therequiredfieldshouldbemarkedasinvalid");
        assert.strictEqual(warnings,1,
            "awarningshouldhavebeendisplayed");

        list.destroy();
    });

    QUnit.test('openavirtualid',asyncfunction(assert){
        assert.expect(1);

        varlist=awaitcreateView({
            View:ListView,
            model:'event',
            data:this.data,
            arch:'<tree><fieldname="name"/></tree>',
        });

        testUtils.mock.intercept(list,'switch_view',function(event){
            assert.deepEqual(_.pick(event.data,'mode','model','res_id','view_type'),{
                mode:'readonly',
                model:'event',
                res_id:'2-20170808020000',
                view_type:'form',
            },"shouldtriggeraswitch_vieweventtotheformviewfortherecordvirtualid");
        });
        testUtils.dom.click(list.$('td:contains(virtual)'));

        list.destroy();
    });

    QUnit.test('pressingenteronlastlineofeditablelistview',asyncfunction(assert){
        assert.expect(7);

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<treeeditable="bottom"><fieldname="foo"/></tree>',
            mockRPC:function(route){
                assert.step(route);
                returnthis._super.apply(this,arguments);
            },
        });

        //clickon3rdline
        awaittestUtils.dom.click(list.$('td:contains(gnap)'));
        assert.hasClass(list.$('tr.o_data_row:eq(2)'),'o_selected_row',
            "3rdrowshouldbeselected");

        //pressenterininput
        awaittestUtils.fields.triggerKeydown(list.$('tr.o_selected_rowinput[name="foo"]'),'enter');
        assert.hasClass(list.$('tr.o_data_row:eq(3)'),'o_selected_row',
            "4rdrowshouldbeselected");
        assert.doesNotHaveClass(list.$('tr.o_data_row:eq(2)'),'o_selected_row',
            "3rdrowshouldnolongerbeselected");

        //pressenteronlastrow
        awaittestUtils.fields.triggerKeydown(list.$('tr.o_selected_rowinput[name="foo"]'),'enter');
        assert.containsN(list,'tr.o_data_row',5,"shouldhavecreateda5throw");

        assert.verifySteps(['/web/dataset/search_read','/web/dataset/call_kw/foo/onchange']);
        list.destroy();
    });

    QUnit.test('pressingtabonlastcellofeditablelistview',asyncfunction(assert){
        assert.expect(9);

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<treeeditable="bottom"><fieldname="foo"/><fieldname="int_field"/></tree>',
            mockRPC:function(route){
                assert.step(route);
                returnthis._super.apply(this,arguments);
            },
        });

        awaittestUtils.dom.click(list.$('td:contains(blip)').last());
        assert.strictEqual(document.activeElement.name,"foo",
            "focusshouldbeonaninputwithname=foo");

        //itwillnotcreateanewlineunlessamodificationismade
        document.activeElement.value="blip-changed";
        $(document.activeElement).trigger({type:'change'});

        awaittestUtils.fields.triggerKeydown(list.$('tr.o_selected_rowinput[name="foo"]'),'tab');
        assert.strictEqual(document.activeElement.name,"int_field",
            "focusshouldbeonaninputwithname=int_field");

        awaittestUtils.fields.triggerKeydown(list.$('tr.o_selected_rowinput[name="foo"]'),'tab');
        assert.hasClass(list.$('tr.o_data_row:eq(4)'),'o_selected_row',
            "5throwshouldbeselected");
        assert.strictEqual(document.activeElement.name,"foo",
            "focusshouldbeonaninputwithname=foo");

        assert.verifySteps(['/web/dataset/search_read',
            '/web/dataset/call_kw/foo/write',
            '/web/dataset/call_kw/foo/read',
            '/web/dataset/call_kw/foo/onchange']);
        list.destroy();
    });

    QUnit.test('navigationwithtabandreadcompletesafterdefault_get',asyncfunction(assert){
        assert.expect(8);

        varonchangeGetPromise=testUtils.makeTestPromise();
        varreadPromise=testUtils.makeTestPromise();

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<treeeditable="bottom"><fieldname="foo"/><fieldname="int_field"/></tree>',
            mockRPC:function(route,args){
                if(args.method){
                    assert.step(args.method);
                }
                varresult=this._super.apply(this,arguments);
                if(args.method==='read'){
                    returnreadPromise.then(function(){
                        returnresult;
                    });
                }
                if(args.method==='onchange'){
                    returnonchangeGetPromise.then(function(){
                        returnresult;
                    });
                }
                returnresult;
            },
        });

        awaittestUtils.dom.click(list.$('td:contains(-4)').last());

        awaittestUtils.fields.editInput(list.$('tr.o_selected_rowinput[name="int_field"]'),'1234');
        awaittestUtils.fields.triggerKeydown(list.$('tr.o_selected_rowinput[name="int_field"]'),'tab');

        onchangeGetPromise.resolve();
        assert.containsN(list,'tbodytr.o_data_row',4,
            "shouldhave4datarows");

        readPromise.resolve();
        awaittestUtils.nextTick();
        assert.containsN(list,'tbodytr.o_data_row',5,
            "shouldhave5datarows");
        assert.strictEqual(list.$('td:contains(1234)').length,1,
            "shouldhaveacellwithnewvalue");

        //wetriggeratabtomovetothesecondcellinthecurrentrow.this
        //operationrequiresthatthis.currentRowisproperlysetinthe
        //listeditablerenderer.
        awaittestUtils.fields.triggerKeydown(list.$('tr.o_selected_rowinput[name="foo"]'),'tab');
        assert.hasClass(list.$('tr.o_data_row:eq(4)'),'o_selected_row',
            "5throwshouldbeselected");

        assert.verifySteps(['write','read','onchange']);
        list.destroy();
    });

    QUnit.test('displaytoolbar',asyncfunction(assert){
        assert.expect(2);

        varlist=awaitcreateView({
            View:ListView,
            model:'event',
            data:this.data,
            arch:'<tree><fieldname="name"/></tree>',
            toolbar:{
                action:[{
                    model_name:'event',
                    name:'Actionevent',
                    type:'ir.actions.server',
                    usage:'ir_actions_server',
                }],
                print:[],
            },
            viewOptions:{
                hasActionMenus:true,
            },
        });


        assert.containsNone(list.el,'div.o_control_panel.o_cp_action_menus');

        awaittestUtils.dom.click(list.$('.o_list_record_selector:firstinput'));

        awaitcpHelpers.toggleActionMenu(list);
        assert.deepEqual(cpHelpers.getMenuItemTexts(list),['Delete','Actionevent']);

        list.destroy();
    });

    QUnit.test('executeActionMenusactionswithcorrectparams(singlepage)',asyncfunction(assert){
        assert.expect(12);

        constlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<tree><fieldname="foo"/></tree>',
            toolbar:{
                action:[{
                    id:44,
                    name:'CustomAction',
                    type:'ir.actions.server',
                }],
                print:[],
            },
            mockRPC:function(route,args){
                if(route==='/web/action/load'){
                    assert.step(JSON.stringify(args));
                    returnPromise.resolve({});
                }
                returnthis._super(...arguments);
            },
            viewOptions:{
                hasActionMenus:true,
            },
        });

        assert.containsNone(list.el,'div.o_control_panel.o_cp_action_menus');

        assert.containsN(list,'.o_data_row',4);

        //selectallrecords
        awaittestUtils.dom.click(list.$('thead.o_list_record_selectorinput'));
        assert.containsN(list,'.o_list_record_selectorinput:checked',5);

        assert.containsOnce(list.el,'div.o_control_panel.o_cp_action_menus');

        awaitcpHelpers.toggleActionMenu(list);
        awaitcpHelpers.toggleMenuItem(list,"CustomAction");

        //unselectfirstrecord(willunselectthetheadcheckboxaswell)
        awaittestUtils.dom.click(list.$('tbody.o_list_record_selector:firstinput'));
        assert.containsN(list,'.o_list_record_selectorinput:checked',3);
        awaitcpHelpers.toggleActionMenu(list);
        awaitcpHelpers.toggleMenuItem(list,"CustomAction");

        //addadomainandselectfirsttworecords
        awaitlist.reload({domain:[['bar','=',true]]});
        assert.containsN(list,'.o_data_row',3);
        assert.containsNone(list,'.o_list_record_selectorinput:checked');

        awaittestUtils.dom.click(list.$('tbody.o_list_record_selector:nth(0)input'));
        awaittestUtils.dom.click(list.$('tbody.o_list_record_selector:nth(1)input'));
        assert.containsN(list,'.o_list_record_selectorinput:checked',2);

        awaitcpHelpers.toggleActionMenu(list);
        awaitcpHelpers.toggleMenuItem(list,"CustomAction");

        assert.verifySteps([
            '{"action_id":44,"context":{"active_id":1,"active_ids":[1,2,3,4],"active_model":"foo","active_domain":[]}}',
            '{"action_id":44,"context":{"active_id":2,"active_ids":[2,3,4],"active_model":"foo","active_domain":[]}}',
            '{"action_id":44,"context":{"active_id":1,"active_ids":[1,2],"active_model":"foo","active_domain":[["bar","=",true]]}}',
        ]);

        list.destroy();
    });

    QUnit.test('executeActionMenusactionswithcorrectparams(multipages)',asyncfunction(assert){
        assert.expect(13);

        constlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<treelimit="2"><fieldname="foo"/></tree>',
            toolbar:{
                action:[{
                    id:44,
                    name:'CustomAction',
                    type:'ir.actions.server',
                }],
                print:[],
            },
            mockRPC:function(route,args){
                if(route==='/web/action/load'){
                    assert.step(JSON.stringify(args));
                    returnPromise.resolve({});
                }
                returnthis._super(...arguments);
            },
            viewOptions:{
                hasActionMenus:true,
            },
        });

        assert.containsNone(list.el,'div.o_control_panel.o_cp_action_menus');
        assert.containsN(list,'.o_data_row',2);

        //selectallrecords
        awaittestUtils.dom.click(list.$('thead.o_list_record_selectorinput'));
        assert.containsN(list,'.o_list_record_selectorinput:checked',3);
        assert.containsOnce(list,'.o_list_selection_box.o_list_select_domain');
        assert.containsOnce(list.el,'div.o_control_panel.o_cp_action_menus');

        awaitcpHelpers.toggleActionMenu(list);
        awaitcpHelpers.toggleMenuItem(list,"CustomAction");

        //selectalldomain
        awaittestUtils.dom.click(list.$('.o_list_selection_box.o_list_select_domain'));
        assert.containsN(list,'.o_list_record_selectorinput:checked',3);

        awaitcpHelpers.toggleActionMenu(list);
        awaitcpHelpers.toggleMenuItem(list,"CustomAction");

        //addadomain
        awaitlist.reload({domain:[['bar','=',true]]});
        assert.containsNone(list,'.o_list_selection_box.o_list_select_domain');

        //selectalldomain
        awaittestUtils.dom.click(list.$('thead.o_list_record_selectorinput'));
        awaittestUtils.dom.click(list.$('.o_list_selection_box.o_list_select_domain'));
        assert.containsN(list,'.o_list_record_selectorinput:checked',3);
        assert.containsNone(list,'.o_list_selection_box.o_list_select_domain');

        awaitcpHelpers.toggleActionMenu(list);
        awaitcpHelpers.toggleMenuItem(list,"CustomAction");

        assert.verifySteps([
            '{"action_id":44,"context":{"active_id":1,"active_ids":[1,2],"active_model":"foo","active_domain":[]}}',
            '{"action_id":44,"context":{"active_id":1,"active_ids":[1,2,3,4],"active_model":"foo","active_domain":[]}}',
            '{"action_id":44,"context":{"active_id":1,"active_ids":[1,2,3],"active_model":"foo","active_domain":[["bar","=",true]]}}',
        ]);

        list.destroy();
    });

    QUnit.test('editlistlineafterlinedeletion',asyncfunction(assert){
        assert.expect(5);

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<treeeditable="top"><fieldname="foo"/><fieldname="int_field"/></tree>',
        });

        awaittestUtils.dom.click(list.$('.o_data_row:nth(2)>td:not(.o_list_record_selector)').first());
        assert.ok(list.$('.o_data_row:nth(2)').is('.o_selected_row'),
            "thirdrowshouldbeinedition");
        awaittestUtils.dom.click(list.$buttons.find('.o_list_button_discard'));
        awaittestUtils.dom.click(list.$buttons.find('.o_list_button_add'));
        assert.ok(list.$('.o_data_row:nth(0)').is('.o_selected_row'),
            "firstrowshouldbeinedition(creation)");
        awaittestUtils.dom.click(list.$buttons.find('.o_list_button_discard'));
        assert.containsNone(list,'.o_selected_row',
            "norowshouldbeselected");
        awaittestUtils.dom.click(list.$('.o_data_row:nth(2)>td:not(.o_list_record_selector)').first());
        assert.ok(list.$('.o_data_row:nth(2)').is('.o_selected_row'),
            "thirdrowshouldbeinedition");
        assert.containsOnce(list,'.o_selected_row',
            "nootherrowshouldbeselected");

        list.destroy();
    });

    QUnit.test('pressingTABineditablelistwithseveralfields[REQUIREFOCUS]',asyncfunction(assert){
        assert.expect(6);

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<treeeditable="bottom">'+
                    '<fieldname="foo"/>'+
                    '<fieldname="int_field"/>'+
                '</tree>',
        });

        awaittestUtils.dom.click(list.$('.o_data_cell:first'));
        assert.hasClass(list.$('.o_data_row:first'),'o_selected_row');
        assert.strictEqual(document.activeElement,list.$('.o_data_row:first.o_data_cell:firstinput')[0]);

        ////Press'Tab'->shouldgotonextcell(stillinfirstrow)
        awaittestUtils.fields.triggerKeydown(list.$('.o_selected_rowinput[name="foo"]'),'tab');
        assert.hasClass(list.$('.o_data_row:first'),'o_selected_row');
        assert.strictEqual(document.activeElement,list.$('.o_data_row:first.o_data_cell:lastinput')[0]);

        ////Press'Tab'->shouldgotonextline(firstcell)
        awaittestUtils.fields.triggerKeydown(list.$('.o_selected_rowinput[name="int_field"]'),'tab');
        assert.hasClass(list.$('.o_data_row:nth(1)'),'o_selected_row');
        assert.strictEqual(document.activeElement,list.$('.o_data_row:nth(1).o_data_cell:firstinput')[0]);

        list.destroy();
    });

    QUnit.test('pressingSHIFT-TABineditablelistwithseveralfields[REQUIREFOCUS]',asyncfunction(assert){
        assert.expect(6);

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<treeeditable="bottom">'+
                    '<fieldname="foo"/>'+
                    '<fieldname="int_field"/>'+
                '</tree>',
        });

        awaittestUtils.dom.click(list.$('.o_data_row:nth(2).o_data_cell:nth(1)'));
        assert.hasClass(list.$('.o_data_row:nth(2)'),'o_selected_row');
        assert.strictEqual(document.activeElement,list.$('.o_data_row:nth(2).o_data_cell:lastinput')[0]);

        //Press'shift-Tab'->shouldgotopreviousline(lastcell)
        list.$('tr.o_selected_rowinput').trigger($.Event('keydown',{which:$.ui.keyCode.TAB,shiftKey:true}));
        awaittestUtils.nextTick();
        assert.hasClass(list.$('.o_data_row:nth(2)'),'o_selected_row');
        assert.strictEqual(document.activeElement,list.$('.o_data_row:nth(2).o_data_cell:firstinput')[0]);

        //Press'shift-Tab'->shouldgotopreviouscell
        list.$('tr.o_selected_rowinput').trigger($.Event('keydown',{which:$.ui.keyCode.TAB,shiftKey:true}));
        awaittestUtils.nextTick();
        assert.hasClass(list.$('.o_data_row:nth(1)'),'o_selected_row');
        assert.strictEqual(document.activeElement,list.$('.o_data_row:nth(1).o_data_cell:lastinput')[0]);

        list.destroy();
    });

    QUnit.test('navigationwithtabandreadonlyfield(nomodification)',asyncfunction(assert){
        //Thistestmakessurethatifwehave2cellsinarow,thefirstin
        //editmode,andthesecondonereadonly,thenifwepressTABwhenthe
        //focusisonthefirst,thenthefocusskipthereadonlycellsand
        //directlygoestothenextlineinstead.
        assert.expect(2);

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<treeeditable="bottom"><fieldname="foo"/><fieldname="int_field"readonly="1"/></tree>',
        });

        //clickonfirsttdandpressTAB
        awaittestUtils.dom.click(list.$('td:contains(yop)').last());

        awaittestUtils.fields.triggerKeydown(list.$('tr.o_selected_rowinput[name="foo"]'),'tab');

        assert.hasClass(list.$('tr.o_data_row:eq(1)'),'o_selected_row',
            "2ndrowshouldbeselected");

        //wedoitagain.Thiswasbrokenbecausethethis.currentRowvariable
        //wasnotproperlyset,andthesecondTABcouldcauseacrash.
        awaittestUtils.fields.triggerKeydown(list.$('tr.o_selected_rowinput[name="foo"]'),'tab');
        assert.hasClass(list.$('tr.o_data_row:eq(2)'),'o_selected_row',
            "3rdrowshouldbeselected");

        list.destroy();
    });

    QUnit.test('navigationwithtabandreadonlyfield(withmodification)',asyncfunction(assert){
        //Thistestmakessurethatifwehave2cellsinarow,thefirstin
        //editmode,andthesecondonereadonly,thenifwepressTABwhenthe
        //focusisonthefirst,thenthefocusskipsthereadonlycellsand
        //directlygoestothenextlineinstead.
        assert.expect(2);

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<treeeditable="bottom"><fieldname="foo"/><fieldname="int_field"readonly="1"/></tree>',
        });

        //clickonfirsttdandpressTAB
        awaittestUtils.dom.click(list.$('td:contains(yop)'));

        //moditythecellcontent
        testUtils.fields.editAndTrigger($(document.activeElement),
            'blip-changed',['change']);

        awaittestUtils.fields.triggerKeydown(list.$('tr.o_selected_rowinput[name="foo"]'),'tab');

        assert.hasClass(list.$('tr.o_data_row:eq(1)'),'o_selected_row',
            "2ndrowshouldbeselected");

        //wedoitagain.Thiswasbrokenbecausethethis.currentRowvariable
        //wasnotproperlyset,andthesecondTABcouldcauseacrash.
        awaittestUtils.fields.triggerKeydown(list.$('tr.o_selected_rowinput[name="foo"]'),'tab');
        assert.hasClass(list.$('tr.o_data_row:eq(2)'),'o_selected_row',
            "3rdrowshouldbeselected");

        list.destroy();
    });

    QUnit.test('navigationwithtabonalistwithcreate="0"',asyncfunction(assert){
        assert.expect(4);

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<treeeditable="bottom"create="0">'+
                        '<fieldname="display_name"/>'+
                    '</tree>',
        });

        assert.containsN(list,'.o_data_row',4,
            "thelistshouldcontain4rows");

        awaittestUtils.dom.click(list.$('.o_data_row:nth(2).o_data_cell:first'));
        assert.hasClass(list.$('.o_data_row:nth(2)'),'o_selected_row',
            "thirdrowshouldbeinedition");

        //Press'Tab'->shouldgotonextline
        //addavalueinthecellbecausetheTabonanemptyfirstcellwouldactivatethenextwidgetintheview
        awaittestUtils.fields.editInput(list.$('.o_selected_rowinput').eq(1),11);
        awaittestUtils.fields.triggerKeydown(list.$('.o_selected_rowinput[name="display_name"]'),'tab');
        assert.hasClass(list.$('.o_data_row:nth(3)'),'o_selected_row',
            "fourthrowshouldbeinedition");

        //Press'Tab'->shouldgobacktofirstlineasthecreateactionisn'tavailable
        awaittestUtils.fields.editInput(list.$('.o_selected_rowinput').eq(1),11);
        awaittestUtils.fields.triggerKeydown(list.$('.o_selected_rowinput[name="display_name"]'),'tab');
        assert.hasClass(list.$('.o_data_row:first'),'o_selected_row',
            "firstrowshouldbeinedition");

        list.destroy();
    });

    QUnit.test('navigationwithtabonaone2manylistwithcreate="0"',asyncfunction(assert){
        assert.expect(4);

        this.data.foo.records[0].o2m=[1,2];
        varform=awaitcreateView({
            View:FormView,
            model:'foo',
            data:this.data,
            arch:'<form><sheet>'+
                    '<fieldname="o2m">'+
                        '<treeeditable="bottom"create="0">'+
                            '<fieldname="display_name"/>'+
                        '</tree>'+
                    '</field>'+
                    '<fieldname="foo"/>'+
                '</sheet></form>',
            res_id:1,
            viewOptions:{
                mode:'edit',
            },
        });

        assert.containsN(form,'.o_field_widget[name=o2m].o_data_row',2,
            "thereshouldbetworecordsinthemany2many");

        awaittestUtils.dom.click(form.$('.o_field_widget[name=o2m].o_data_cell:first'));
        assert.hasClass(form.$('.o_field_widget[name=o2m].o_data_row:first'),'o_selected_row',
            "firstrowshouldbeinedition");

        //Press'Tab'->shouldgotonextline
        awaittestUtils.fields.triggerKeydown(form.$('.o_field_widget[name=o2m].o_selected_rowinput'),'tab');
        assert.hasClass(form.$('.o_field_widget[name=o2m].o_data_row:nth(1)'),'o_selected_row',
            "secondrowshouldbeinedition");

        //Press'Tab'->shouldgetoutoftheonetomanyandgotothenextfieldoftheform
        awaittestUtils.fields.triggerKeydown(form.$('.o_field_widget[name=o2m].o_selected_rowinput'),'tab');
        //useofowlCompatibilityNextTickbecausethex2manycontrolpanelisupdatedtwice
        awaittestUtils.owlCompatibilityNextTick();
        assert.strictEqual(document.activeElement,form.$('input[name="foo"]')[0],
            "thenextfieldshouldbeselected");

        form.destroy();
    });

    QUnit.test('edition,thennavigationwithtab(withareadonlyfield)',asyncfunction(assert){
        //Thistestmakessurethatifwehave2cellsinarow,thefirstin
        //editmode,andthesecondonereadonly,thenifweeditandpressTAB,
        //(beforedebounce),thesaveoperationisproperlydone(before
        //selectingthenextrow)
        assert.expect(4);

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<treeeditable="bottom"><fieldname="foo"/><fieldname="int_field"readonly="1"/></tree>',
            mockRPC:function(route,args){
                if(args.method){
                    assert.step(args.method);
                }
                returnthis._super.apply(this,arguments);
            },
            fieldDebounce:1,
        });

        //clickonfirsttdandpressTAB
        awaittestUtils.dom.click(list.$('td:contains(yop)'));
        awaittestUtils.fields.editSelect(list.$('tr.o_selected_rowinput[name="foo"]'),'newvalue');
        awaittestUtils.fields.triggerKeydown(list.$('tr.o_selected_rowinput[name="foo"]'),'tab');

        assert.strictEqual(list.$('tbodytr:firsttd:contains(newvalue)').length,1,
            "shouldhavethenewvaluevisibleindom");
        assert.verifySteps(["write","read"]);
        list.destroy();
    });

    QUnit.test('edition,thennavigationwithtab(withareadonlyfieldandonchange)',asyncfunction(assert){
        //Thistestmakessurethatifwehavearead-onlycellinarow,in
        //casethekeyboardnavigationmoveoveritandthereaunsavedchanges
        //(whichwilltriggeranonchange),thefocusofthenextactivable
        //fieldwillnotcrash
        assert.expect(4);

        this.data.bar.onchanges={
            o2m:function(){},
        };
        this.data.bar.fields.o2m={string:"O2Mfield",type:"one2many",relation:"foo"};
        this.data.bar.records[0].o2m=[1,4];

        varform=awaitcreateView({
            View:FormView,
            model:'bar',
            res_id:1,
            data:this.data,
            arch:'<form>'+
                    '<group>'+
                        '<fieldname="display_name"/>'+
                        '<fieldname="o2m">'+
                            '<treeeditable="bottom">'+
                                '<fieldname="foo"/>'+
                                '<fieldname="date"readonly="1"/>'+
                                '<fieldname="int_field"/>'+
                            '</tree>'+
                        '</field>'+
                    '</group>'+
                '</form>',
            mockRPC:function(route,args){
                if(args.method==='onchange'){
                    assert.step(args.method+':'+args.model);
                }
                returnthis._super.apply(this,arguments);
            },
            fieldDebounce:1,
            viewOptions:{
                mode:'edit',
            },
        });

        varjq_evspecial_focus_trigger=$.event.special.focus.trigger;
        //AsKeyboardEventwillbetriggeredbyJSandnotfromthe
        //User-Agentitself,thefocuseventwillnottriggerdefault
        //action(eventnotbeingtrusted),weneedtomanuallytrigger
        //'change'eventonthecurrentlyfocusedelement
        $.event.special.focus.trigger=function(){
            if(this!==document.activeElement&&this.focus){
                varactiveElement=document.activeElement;
                this.focus();
                $(activeElement).trigger('change');
            }
        };

        //editablelist,clickonfirsttdandpressTAB
        awaittestUtils.dom.click(form.$('.o_data_cell:contains(yop)'));
        assert.strictEqual(document.activeElement,form.$('tr.o_selected_rowinput[name="foo"]')[0],
            "focusshouldbeonaninputwithname=foo");
        awaittestUtils.fields.editInput(form.$('tr.o_selected_rowinput[name="foo"]'),'newvalue');
        vartabEvent=$.Event("keydown",{which:$.ui.keyCode.TAB});
        awaittestUtils.dom.triggerEvents(form.$('tr.o_selected_rowinput[name="foo"]'),[tabEvent]);
        assert.strictEqual(document.activeElement,form.$('tr.o_selected_rowinput[name="int_field"]')[0],
            "focusshouldbeonaninputwithname=int_field");

        //RestoreoriginjQueryspecialtriggerfor'focus'
        $.event.special.focus.trigger=jq_evspecial_focus_trigger;

        assert.verifySteps(["onchange:bar"],"onchangemethodshouldhavebeencalled");
        form.destroy();
    });

    QUnit.test('pressingSHIFT-TABineditablelistwithareadonlyfield[REQUIREFOCUS]',asyncfunction(assert){
        assert.expect(4);

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<treeeditable="bottom">'+
                    '<fieldname="foo"/>'+
                    '<fieldname="int_field"readonly="1"/>'+
                    '<fieldname="qux"/>'+
                '</tree>',
        });

        //starton'qux',line3
        awaittestUtils.dom.click(list.$('.o_data_row:nth(2).o_data_cell:nth(2)'));
        assert.hasClass(list.$('.o_data_row:nth(2)'),'o_selected_row');
        assert.strictEqual(document.activeElement,list.$('.o_data_row:nth(2).o_data_cellinput[name=qux]')[0]);

        //Press'shift-Tab'->shouldgotofirstcell(sameline)
        $(document.activeElement).trigger({type:'keydown',which:$.ui.keyCode.TAB,shiftKey:true});
        awaittestUtils.nextTick();
        assert.hasClass(list.$('.o_data_row:nth(2)'),'o_selected_row');
        assert.strictEqual(document.activeElement,list.$('.o_data_row:nth(2).o_data_cellinput[name=foo]')[0]);

        list.destroy();
    });

    QUnit.test('pressingSHIFT-TABineditablelistwithareadonlyfieldinfirstcolumn[REQUIREFOCUS]',asyncfunction(assert){
        assert.expect(4);

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<treeeditable="bottom">'+
                    '<fieldname="int_field"readonly="1"/>'+
                    '<fieldname="foo"/>'+
                    '<fieldname="qux"/>'+
                '</tree>',
        });

        //starton'foo',line3
        awaittestUtils.dom.click(list.$('.o_data_row:nth(2).o_data_cell:nth(1)'));
        assert.hasClass(list.$('.o_data_row:nth(2)'),'o_selected_row');
        assert.strictEqual(document.activeElement,list.$('.o_data_row:nth(2).o_data_cellinput[name=foo]')[0]);

        //Press'shift-Tab'->shouldgotopreviousline(lastcell)
        $(document.activeElement).trigger({type:'keydown',which:$.ui.keyCode.TAB,shiftKey:true});
        awaittestUtils.nextTick();
        assert.hasClass(list.$('.o_data_row:nth(1)'),'o_selected_row');
        assert.strictEqual(document.activeElement,list.$('.o_data_row:nth(1).o_data_cellinput[name=qux]')[0]);

        list.destroy();
    });

    QUnit.test('pressingSHIFT-TABineditablelistwithareadonlyfieldinlastcolumn[REQUIREFOCUS]',asyncfunction(assert){
        assert.expect(4);

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<treeeditable="bottom">'+
                    '<fieldname="int_field"/>'+
                    '<fieldname="foo"/>'+
                    '<fieldname="qux"readonly="1"/>'+
                '</tree>',
        });

        //starton'int_field',line3
        awaittestUtils.dom.click(list.$('.o_data_row:nth(2).o_data_cell:first'));
        assert.hasClass(list.$('.o_data_row:nth(2)'),'o_selected_row');
        assert.strictEqual(document.activeElement,list.$('.o_data_row:nth(2).o_data_cellinput[name=int_field]')[0]);

        //Press'shift-Tab'->shouldgotopreviousline('foo'field)
        $(document.activeElement).trigger({type:'keydown',which:$.ui.keyCode.TAB,shiftKey:true});
        awaittestUtils.nextTick();
        assert.hasClass(list.$('.o_data_row:nth(1)'),'o_selected_row');
        assert.strictEqual(document.activeElement,list.$('.o_data_row:nth(1).o_data_cellinput[name=foo]')[0]);

        list.destroy();
    });

    QUnit.test('skipinvisiblefieldswhennavigatinglistviewwithTAB',asyncfunction(assert){
        assert.expect(2);

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<treeeditable="bottom">'+
                    '<fieldname="foo"/>'+
                    '<fieldname="bar"invisible="1"/>'+
                    '<fieldname="int_field"/>'+
                '</tree>',
            res_id:1,
        });

        awaittestUtils.dom.click(list.$('td:contains(gnap)'));
        assert.strictEqual(list.$('input[name="foo"]')[0],document.activeElement,
            "fooshouldbefocused");
        awaittestUtils.fields.triggerKeydown(list.$('input[name="foo"]'),'tab');
        assert.strictEqual(list.$('input[name="int_field"]')[0],document.activeElement,
            "int_fieldshouldbefocused");

        list.destroy();
    });

    QUnit.test('skipbuttonswhennavigatinglistviewwithTAB(end)',asyncfunction(assert){
        assert.expect(2);

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<treeeditable="bottom">'+
                    '<fieldname="foo"/>'+
                    '<buttonname="kikou"string="Kikou"type="object"/>'+
                '</tree>',
            res_id:1,
        });

        awaittestUtils.dom.click(list.$('tbodytr:eq(2)td:eq(1)'));
        assert.strictEqual(list.$('tbodytr:eq(2)input[name="foo"]')[0],document.activeElement,
            "fooshouldbefocused");
        awaittestUtils.fields.triggerKeydown(list.$('tbodytr:eq(2)input[name="foo"]'),'tab');
        assert.strictEqual(list.$('tbodytr:eq(3)input[name="foo"]')[0],document.activeElement,
            "nextlineshouldbeselected");

        list.destroy();
    });

    QUnit.test('skipbuttonswhennavigatinglistviewwithTAB(middle)',asyncfunction(assert){
        assert.expect(2);

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<treeeditable="bottom">'+
                    //Addingabuttoncolumnmakesconversionsbetweencolumnandfieldpositiontrickier
                    '<buttonname="kikou"string="Kikou"type="object"/>'+
                    '<fieldname="foo"/>'+
                    '<buttonname="kikou"string="Kikou"type="object"/>'+
                    '<fieldname="int_field"/>'+
                '</tree>',
            res_id:1,
        });

        awaittestUtils.dom.click(list.$('tbodytr:eq(2)td:eq(2)'));
        assert.strictEqual(list.$('tbodytr:eq(2)input[name="foo"]')[0],document.activeElement,
            "fooshouldbefocused");
        awaittestUtils.fields.triggerKeydown(list.$('tbodytr:eq(2)input[name="foo"]'),'tab');
        assert.strictEqual(list.$('tbodytr:eq(2)input[name="int_field"]')[0],document.activeElement,
            "int_fieldshouldbefocused");

        list.destroy();
    });

    QUnit.test('navigation:notmovingdownwithkeydown',asyncfunction(assert){
        assert.expect(2);

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<treeeditable="bottom"><fieldname="foo"/></tree>',
        });

        awaittestUtils.dom.click(list.$('td:contains(yop)'));
        assert.hasClass(list.$('tr.o_data_row:eq(0)'),'o_selected_row',
            "1strowshouldbeselected");
        awaittestUtils.fields.triggerKeydown(list.$('tr.o_selected_rowinput[name="foo"]'),'down');
        assert.hasClass(list.$('tr.o_data_row:eq(0)'),'o_selected_row',
            "1strowshouldstillbeselected");
        list.destroy();
    });

    QUnit.test('navigation:movingrightwithkeydownfromtextfielddoesnotmovethefocus',asyncfunction(assert){
        assert.expect(6);

        this.data.foo.fields.foo.type='text';
        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:
                '<treeeditable="bottom">'+
                    '<fieldname="foo"/>'+
                    '<fieldname="bar"/>'+
                '</tree>',
        });

        awaittestUtils.dom.click(list.$('td:contains(yop)'));
        vartextarea=list.$('textarea[name="foo"]')[0];
        assert.strictEqual(document.activeElement,textarea,
            "textareashouldbefocused");
        assert.strictEqual(textarea.selectionStart, 0,
            "textareaselectionstartshouldbeatthebeginning");
        assert.strictEqual(textarea.selectionEnd, 3,
            "textareaselectionendshouldbeattheend");
        textarea.selectionStart=3;//Simulatebrowserkeyboardrightbehavior(unselect)
        assert.strictEqual(document.activeElement,textarea,
            "textareashouldstillbefocused");
        assert.ok(textarea.selectionStart===3&&textarea.selectionEnd===3,
            "textareavalue('yop')shouldnotbeselectedandcursorshouldbeattheend");
        awaittestUtils.fields.triggerKeydown($(textarea),'right');
        assert.strictEqual(document.activeElement,list.$('textarea[name="foo"]')[0],
            "nextfield(checkbox)shouldnowbefocused");
        list.destroy();
    });

    QUnit.test('discardingchangesinarowproperlyupdatestherendering',asyncfunction(assert){
        assert.expect(3);

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:
                '<treeeditable="top">'+
                    '<fieldname="foo"/>'+
                '</tree>',
        });

        assert.strictEqual(list.$('.o_data_cell:first').text(),"yop",
            "firstcellshouldcontain'yop'");

        awaittestUtils.dom.click(list.$('.o_data_cell:first'));
        awaittestUtils.fields.editInput(list.$('input[name="foo"]'),"hello");
        awaittestUtils.dom.click(list.$buttons.find('.o_list_button_discard'));
        assert.strictEqual($('.modal:visible').length,1,
            "amodaltoaskfordiscardshouldbevisible");

        awaittestUtils.dom.click($('.modal:visible.btn-primary'));
        assert.strictEqual(list.$('.o_data_cell:first').text(),"yop",
            "firstcellshouldstillcontain'yop'");

        list.destroy();
    });

    QUnit.test('numbersinlistareright-aligned',asyncfunction(assert){
        assert.expect(2);

        varcurrencies={};
        _.each(this.data.res_currency.records,function(currency){
            currencies[currency.id]=currency;
        });
        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:
                '<treeeditable="top">'+
                    '<fieldname="foo"/>'+
                    '<fieldname="qux"/>'+
                    '<fieldname="amount"widget="monetary"/>'+
                    '<fieldname="currency_id"invisible="1"/>'+
                '</tree>',
            session:{
                currencies:currencies,
            },
        });

        varnbCellRight=_.filter(list.$('.o_data_row:first>.o_data_cell'),function(el){
            varstyle=window.getComputedStyle(el);
            returnstyle.textAlign==='right';
        }).length;
        assert.strictEqual(nbCellRight,2,
            "thereshouldbetworight-alignedcells");

        awaittestUtils.dom.click(list.$('.o_data_cell:first'));

        varnbInputRight=_.filter(list.$('.o_data_row:first>.o_data_cellinput'),function(el){
            varstyle=window.getComputedStyle(el);
            returnstyle.textAlign==='right';
        }).length;
        assert.strictEqual(nbInputRight,2,
            "thereshouldbetworight-alignedinput");

        list.destroy();
    });

    QUnit.test('groupedlistwithanothergroupedlistparent,clickunfold',asyncfunction(assert){
        assert.expect(3);
        this.data.bar.fields={
            cornichon:{string:'cornichon',type:'char'},
        };

        varrec=this.data.bar.records[0];
        //createrecordstohavethesearchmorebutton
        varnewRecs=[];
        for(vari=0;i<8;i++){
            varnewRec=_.extend({},rec);
            newRec.id=1+i;
            newRec.cornichon='extrafin';
            newRecs.push(newRec);
        }
        this.data.bar.records=newRecs;

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<treeeditable="top"><fieldname="foo"/><fieldname="m2o"/></tree>',
            groupBy:['bar'],
            archs:{
                'bar,false,list':'<tree><fieldname="cornichon"/></tree>',
                'bar,false,search':'<search><filtercontext="{\'group_by\':\'cornichon\'}"string="cornichon"/></search>',
            },
        });

        awaitlist.update({groupBy:[]});

        awaittestUtils.dom.clickFirst(list.$('.o_data_cell'));

        awaittestUtils.fields.many2one.searchAndClickItem('m2o',{item:'SearchMore'});

        assert.containsOnce($('body'),'.modal-content');

        assert.containsNone($('body'),'.modal-content.o_group_name','listinmodalnotgrouped');

        awaittestUtils.dom.click($('body.modal-contentbutton:contains(GroupBy)'));

        awaittestUtils.dom.click($('body.modal-content.o_menu_itema:contains(cornichon)'));

        awaittestUtils.dom.click($('body.modal-content.o_group_header'));

        assert.containsOnce($('body'),'.modal-content.o_group_open');

        list.destroy();
    });

    QUnit.test('fieldvaluesareescaped',asyncfunction(assert){
        assert.expect(1);
        varvalue='<script>throwError();</script>';

        this.data.foo.records[0].foo=value;

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<treeeditable="top"><fieldname="foo"/></tree>',
        });

        assert.strictEqual(list.$('.o_data_cell:first').text(),value,
            "valueshouldhavebeenescaped");

        list.destroy();
    });

    QUnit.test('pressingESCdiscardthecurrentlinechanges',asyncfunction(assert){
        assert.expect(4);

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<treeeditable="top"><fieldname="foo"/></tree>',
        });

        awaittestUtils.dom.click(list.$buttons.find('.o_list_button_add'));
        assert.containsN(list,'tr.o_data_row',5,
            "shouldcurrentlyaddinga5thdatarow");

        awaittestUtils.fields.triggerKeydown(list.$('input[name="foo"]'),'escape');
        assert.containsN(list,'tr.o_data_row',4,
            "shouldhaveonly4datarowafterescape");
        assert.containsNone(list,'tr.o_data_row.o_selected_row',
            "norowsshouldbeselected");
        assert.ok(!list.$buttons.find('.o_list_button_save').is(':visible'),
            "shouldnothaveavisiblesavebutton");
        list.destroy();
    });

    QUnit.test('pressingESCdiscardthecurrentlinechanges(withrequired)',asyncfunction(assert){
        assert.expect(4);

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<treeeditable="top"><fieldname="foo"required="1"/></tree>',
        });

        awaittestUtils.dom.click(list.$buttons.find('.o_list_button_add'));
        assert.containsN(list,'tr.o_data_row',5,
            "shouldcurrentlyaddinga5thdatarow");

        awaittestUtils.fields.triggerKeydown(list.$('input[name="foo"]'),'escape');
        assert.containsN(list,'tr.o_data_row',4,
            "shouldhaveonly4datarowafterescape");
        assert.containsNone(list,'tr.o_data_row.o_selected_row',
            "norowsshouldbeselected");
        assert.ok(!list.$buttons.find('.o_list_button_save').is(':visible'),
            "shouldnothaveavisiblesavebutton");
        list.destroy();
    });

    QUnit.test('fieldwithpasswordattribute',asyncfunction(assert){
        assert.expect(2);

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<tree><fieldname="foo"password="True"/></tree>',
        });

        assert.strictEqual(list.$('td.o_data_cell:eq(0)').text(),'***',
            "shoulddisplaystringaspassword");
        assert.strictEqual(list.$('td.o_data_cell:eq(1)').text(),'****',
            "shoulddisplaystringaspassword");

        list.destroy();
    });

    QUnit.test('listwithhandlewidget',asyncfunction(assert){
        assert.expect(11);

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<tree>'+
                    '<fieldname="int_field"widget="handle"/>'+
                    '<fieldname="amount"widget="float"digits="[5,0]"/>'+
                  '</tree>',
            mockRPC:function(route,args){
                if(route==='/web/dataset/resequence'){
                    assert.strictEqual(args.offset,-4,
                        "shouldwritethesequencestartingfromthelowestcurrentone");
                    assert.strictEqual(args.field,'int_field',
                        "shouldwritetherightfieldassequence");
                    assert.deepEqual(args.ids,[4,2,3],
                        "shouldwritethesequenceincorrectorder");
                    returnPromise.resolve();
                }
                returnthis._super.apply(this,arguments);
            },
        });

        assert.strictEqual(list.$('tbodytr:eq(0)td:last').text(),'1200',
            "defaultfirstrecordshouldhaveamount1200");
        assert.strictEqual(list.$('tbodytr:eq(1)td:last').text(),'500',
            "defaultsecondrecordshouldhaveamount500");
        assert.strictEqual(list.$('tbodytr:eq(2)td:last').text(),'300',
            "defaultthirdrecordshouldhaveamount300");
        assert.strictEqual(list.$('tbodytr:eq(3)td:last').text(),'0',
            "defaultfourthrecordshouldhaveamount0");

        //Draganddropthefourthlineinsecondposition
        awaittestUtils.dom.dragAndDrop(
            list.$('.ui-sortable-handle').eq(3),
            list.$('tbodytr').first(),
            {position:'bottom'}
        );

        assert.strictEqual(list.$('tbodytr:eq(0)td:last').text(),'1200',
            "newfirstrecordshouldhaveamount1200");
        assert.strictEqual(list.$('tbodytr:eq(1)td:last').text(),'0',
            "newsecondrecordshouldhaveamount0");
        assert.strictEqual(list.$('tbodytr:eq(2)td:last').text(),'500',
            "newthirdrecordshouldhaveamount500");
        assert.strictEqual(list.$('tbodytr:eq(3)td:last').text(),'300',
            "newfourthrecordshouldhaveamount300");

        list.destroy();
    });

    QUnit.test('resultofconsecutiveresequencesiscorrectlysorted',asyncfunction(assert){
        assert.expect(9);
        this.data={//wewantthedatatobeminimaltohaveaminimaltest
            foo:{
                fields:{int_field:{string:"int_field",type:"integer",sortable:true}},
                records:[
                    {id:1,int_field:11},
                    {id:2,int_field:12},
                    {id:3,int_field:13},
                    {id:4,int_field:14},
                ]
            }
        };
        varmoves=0;
        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<tree>'+
                    '<fieldname="int_field"widget="handle"/>'+
                    '<fieldname="id"/>'+
                  '</tree>',
            mockRPC:function(route,args){
                if(route==='/web/dataset/resequence'){
                    if(moves===0){
                        assert.deepEqual(args,{
                            context:{},
                            model:"foo",
                            ids:[4,3],
                            offset:13,
                            field:"int_field",
                        });
                    }
                    if(moves===1){
                        assert.deepEqual(args,{
                            context:{},
                            model:"foo",
                            ids:[4,2],
                            offset:12,
                            field:"int_field",
                        });
                    }
                    if(moves===2){
                        assert.deepEqual(args,{
                            context:{},
                            model:"foo",
                            ids:[2,4],
                            offset:12,
                            field:"int_field",
                        });
                    }
                    if(moves===3){
                        assert.deepEqual(args,{
                            context:{},
                            model:"foo",
                            ids:[4,2],
                            offset:12,
                            field:"int_field",
                        });
                    }
                    moves+=1;
                }
                returnthis._super.apply(this,arguments);
            },
        });
        assert.strictEqual(list.$('tbodytrtd.o_list_number').text(),'1234',
            "defaultshouldbesortedbyid");
        awaittestUtils.dom.dragAndDrop(
            list.$('.ui-sortable-handle').eq(3),
            list.$('tbodytr').eq(2),
            {position:'top'}
        );
        assert.strictEqual(list.$('tbodytrtd.o_list_number').text(),'1243',
            "theint_field(sequence)shouldhavebeencorrectlyupdated");

        awaittestUtils.dom.dragAndDrop(
            list.$('.ui-sortable-handle').eq(2),
            list.$('tbodytr').eq(1),
            {position:'top'}
        );
        assert.deepEqual(list.$('tbodytrtd.o_list_number').text(),'1423',
            "theint_field(sequence)shouldhavebeencorrectlyupdated");

        awaittestUtils.dom.dragAndDrop(
            list.$('.ui-sortable-handle').eq(1),
            list.$('tbodytr').eq(3),
            {position:'top'}
        );
        assert.deepEqual(list.$('tbodytrtd.o_list_number').text(),'1243',
            "theint_field(sequence)shouldhavebeencorrectlyupdated");

        awaittestUtils.dom.dragAndDrop(
            list.$('.ui-sortable-handle').eq(2),
            list.$('tbodytr').eq(1),
            {position:'top'}
        );
        assert.deepEqual(list.$('tbodytrtd.o_list_number').text(),'1423',
            "theint_field(sequence)shouldhavebeencorrectlyupdated");
        list.destroy();
    });

    QUnit.test('editablelistwithhandlewidget',asyncfunction(assert){
        assert.expect(12);

        //resequencemakessenseonasequencefield,notonarbitraryfields
        this.data.foo.records[0].int_field=0;
        this.data.foo.records[1].int_field=1;
        this.data.foo.records[2].int_field=2;
        this.data.foo.records[3].int_field=3;

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<treeeditable="top"default_order="int_field">'+
                    '<fieldname="int_field"widget="handle"/>'+
                    '<fieldname="amount"widget="float"digits="[5,0]"/>'+
                  '</tree>',
            mockRPC:function(route,args){
                if(route==='/web/dataset/resequence'){
                    assert.strictEqual(args.offset,1,
                        "shouldwritethesequencestartingfromthelowestcurrentone");
                    assert.strictEqual(args.field,'int_field',
                        "shouldwritetherightfieldassequence");
                    assert.deepEqual(args.ids,[4,2,3],
                        "shouldwritethesequenceincorrectorder");
                }
                returnthis._super.apply(this,arguments);
            },
        });

        assert.strictEqual(list.$('tbodytr:eq(0)td:last').text(),'1200',
            "defaultfirstrecordshouldhaveamount1200");
        assert.strictEqual(list.$('tbodytr:eq(1)td:last').text(),'500',
            "defaultsecondrecordshouldhaveamount500");
        assert.strictEqual(list.$('tbodytr:eq(2)td:last').text(),'300',
            "defaultthirdrecordshouldhaveamount300");
        assert.strictEqual(list.$('tbodytr:eq(3)td:last').text(),'0',
            "defaultfourthrecordshouldhaveamount0");

        //Draganddropthefourthlineinsecondposition
        awaittestUtils.dom.dragAndDrop(
            list.$('.ui-sortable-handle').eq(3),
            list.$('tbodytr').first(),
            {position:'bottom'}
        );

        assert.strictEqual(list.$('tbodytr:eq(0)td:last').text(),'1200',
            "newfirstrecordshouldhaveamount1200");
        assert.strictEqual(list.$('tbodytr:eq(1)td:last').text(),'0',
            "newsecondrecordshouldhaveamount0");
        assert.strictEqual(list.$('tbodytr:eq(2)td:last').text(),'500',
            "newthirdrecordshouldhaveamount500");
        assert.strictEqual(list.$('tbodytr:eq(3)td:last').text(),'300',
            "newfourthrecordshouldhaveamount300");

        awaittestUtils.dom.click(list.$('tbodytr:eq(1)td:last'));

        assert.strictEqual(list.$('tbodytr:eq(1)td:lastinput').val(),'0',
            "theeditedrecordshouldbethegoodone");

        list.destroy();
    });

    QUnit.test('editablelist,handlewidgetlocksandunlocksonsort',asyncfunction(assert){
        assert.expect(6);

        //weneedanothersortablefieldtolock/unlockthehandle
        this.data.foo.fields.amount.sortable=true;
        //resequencemakessenseonasequencefield,notonarbitraryfields
        this.data.foo.records[0].int_field=0;
        this.data.foo.records[1].int_field=1;
        this.data.foo.records[2].int_field=2;
        this.data.foo.records[3].int_field=3;

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<treeeditable="top"default_order="int_field">'+
                    '<fieldname="int_field"widget="handle"/>'+
                    '<fieldname="amount"widget="float"/>'+
                  '</tree>',
        });

        assert.strictEqual(list.$('tbodyspan[name="amount"]').text(),'1200.00500.00300.000.00',
            "defaultshouldbesortedbyint_field");

        //Draganddropthefourthlineinsecondposition
        awaittestUtils.dom.dragAndDrop(
            list.$('.ui-sortable-handle').eq(3),
            list.$('tbodytr').first(),
            {position:'bottom'}
        );

        //Handleshouldbeunlockedatthispoint
        assert.strictEqual(list.$('tbodyspan[name="amount"]').text(),'1200.000.00500.00300.00',
            "draganddropshouldhavesucceeded,asthehandleisunlocked");

        //Sortingbyafielddifferentforint_fieldshouldlockthehandle
        awaittestUtils.dom.click(list.$('.o_column_sortable').eq(1));

        assert.strictEqual(list.$('tbodyspan[name="amount"]').text(),'0.00300.00500.001200.00',
            "shouldhavebeensortedbyamount");

        //Draganddropthefourthlineinsecondposition(not)
        awaittestUtils.dom.dragAndDrop(
            list.$('.ui-sortable-handle').eq(3),
            list.$('tbodytr').first(),
            {position:'bottom'}
        );

        assert.strictEqual(list.$('tbodyspan[name="amount"]').text(),'0.00300.00500.001200.00',
            "draganddropshouldhavefailedasthehandleislocked");

        //Sortingbyint_fieldshouldunlockthehandle
        awaittestUtils.dom.click(list.$('.o_column_sortable').eq(0));

        assert.strictEqual(list.$('tbodyspan[name="amount"]').text(),'1200.000.00500.00300.00',
            "recordsshouldbeorderedasperthepreviousresequence");

        //Draganddropthefourthlineinsecondposition
        awaittestUtils.dom.dragAndDrop(
            list.$('.ui-sortable-handle').eq(3),
            list.$('tbodytr').first(),
            {position:'bottom'}
        );

        assert.strictEqual(list.$('tbodyspan[name="amount"]').text(),'1200.00300.000.00500.00',
            "draganddropshouldhaveworkedasthehandleisunlocked");

        list.destroy();
    });

    QUnit.test('editablelistwithhandlewidgetwithslownetwork',asyncfunction(assert){
        assert.expect(15);

        //resequencemakessenseonasequencefield,notonarbitraryfields
        this.data.foo.records[0].int_field=0;
        this.data.foo.records[1].int_field=1;
        this.data.foo.records[2].int_field=2;
        this.data.foo.records[3].int_field=3;

        varprom=testUtils.makeTestPromise();

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<treeeditable="top">'+
                    '<fieldname="int_field"widget="handle"/>'+
                    '<fieldname="amount"widget="float"digits="[5,0]"/>'+
                  '</tree>',
            mockRPC:function(route,args){
                if(route==='/web/dataset/resequence'){
                    var_super=this._super.bind(this);
                    assert.strictEqual(args.offset,1,
                        "shouldwritethesequencestartingfromthelowestcurrentone");
                    assert.strictEqual(args.field,'int_field',
                        "shouldwritetherightfieldassequence");
                    assert.deepEqual(args.ids,[4,2,3],
                        "shouldwritethesequenceincorrectorder");
                    returnprom.then(function(){
                        return_super(route,args);
                    });
                }
                returnthis._super.apply(this,arguments);
            },
        });
        assert.strictEqual(list.$('tbodytr:eq(0)td:last').text(),'1200',
            "defaultfirstrecordshouldhaveamount1200");
        assert.strictEqual(list.$('tbodytr:eq(1)td:last').text(),'500',
            "defaultsecondrecordshouldhaveamount500");
        assert.strictEqual(list.$('tbodytr:eq(2)td:last').text(),'300',
            "defaultthirdrecordshouldhaveamount300");
        assert.strictEqual(list.$('tbodytr:eq(3)td:last').text(),'0',
            "defaultfourthrecordshouldhaveamount0");

        //draganddropthefourthlineinsecondposition
        awaittestUtils.dom.dragAndDrop(
            list.$('.ui-sortable-handle').eq(3),
            list.$('tbodytr').first(),
            {position:'bottom'}
        );

        //editmovedrowbeforetheendofresequence
        awaittestUtils.dom.click(list.$('tbodytr:eq(3)td:last'));
        awaittestUtils.nextTick();

        assert.strictEqual(list.$('tbodytr:eq(3)td:lastinput').length,0,
            "shouldn'teditthelinebeforeresequence");

        prom.resolve();
        awaittestUtils.nextTick();

        assert.strictEqual(list.$('tbodytr:eq(3)td:lastinput').length,1,
            "shouldeditthelineafterresequence");

        assert.strictEqual(list.$('tbodytr:eq(3)td:lastinput').val(),'300',
            "fourthrecordshouldhaveamount300");

        awaittestUtils.fields.editInput(list.$('tbodytr:eq(3)td:lastinput'),301);
        awaittestUtils.dom.click(list.$('tbodytr:eq(0)td:last'));

        awaittestUtils.dom.click(list.$buttons.find('.o_list_button_save'));

        assert.strictEqual(list.$('tbodytr:eq(0)td:last').text(),'1200',
            "firstrecordshouldhaveamount1200");
        assert.strictEqual(list.$('tbodytr:eq(1)td:last').text(),'0',
            "secondrecordshouldhaveamount1");
        assert.strictEqual(list.$('tbodytr:eq(2)td:last').text(),'500',
            "thirdrecordshouldhaveamount500");
        assert.strictEqual(list.$('tbodytr:eq(3)td:last').text(),'301',
            "fourthrecordshouldhaveamount301");

        awaittestUtils.dom.click(list.$('tbodytr:eq(3)td:last'));
        assert.strictEqual(list.$('tbodytr:eq(3)td:lastinput').val(),'301',
            "fourthrecordshouldhaveamount301");

        list.destroy();
    });

    QUnit.test('listwithhandlewidget,create,moveanddiscard',asyncfunction(assert){
        //Whentherearelessthan4recordsinthetable,emptylinesareadded
        //tohaveatleast4rows.Thistestensuresthattheemptylineadded
        //whenanewrecordisdiscardediscorrectlyaddedonthebottomof
        //thelist,evenifthediscardedrecordwasn't.
        assert.expect(11);

        constlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:`
                <treeeditable="bottom">
                    <fieldname="int_field"widget="handle"/>
                    <fieldname="foo"required="1"/>
                </tree>`,
            domain:[['bar','=',false]],
        });

        assert.containsOnce(list,'.o_data_row');
        assert.containsN(list,'tbodytr',4);

        awaittestUtils.dom.click(list.$('.o_list_button_add'));
        assert.containsN(list,'.o_data_row',2);
        assert.doesNotHaveClass(list.$('.o_data_row:first'),'o_selected_row');
        assert.hasClass(list.$('.o_data_row:nth(1)'),'o_selected_row');

        //Draganddropthefirstlineaftercreatingrecordrow
        awaittestUtils.dom.dragAndDrop(
            list.$('.ui-sortable-handle').eq(0),
            list.$('tbodytr.o_data_row').eq(1),
            {position:'bottom'}
        );
        assert.containsN(list,'.o_data_row',2);
        assert.hasClass(list.$('.o_data_row:first'),'o_selected_row');
        assert.doesNotHaveClass(list.$('.o_data_row:nth(1)'),'o_selected_row');

        awaittestUtils.dom.click(list.$('.o_list_button_discard'));
        assert.containsOnce(list,'.o_data_row');
        assert.hasClass(list.$('tbodytr:first'),'o_data_row');
        assert.containsN(list,'tbodytr',4);

        list.destroy();
    });

    QUnit.test('multipleclicksonAdddonotcreateinvalidrows',asyncfunction(assert){
        assert.expect(3);

        this.data.foo.onchanges={
            m2o:function(){},
        };

        varprom=testUtils.makeTestPromise();
        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<treeeditable="top"><fieldname="m2o"required="1"/></tree>',
            mockRPC:function(route,args){
                varresult=this._super.apply(this,arguments);
                if(args.method==='onchange'){
                    returnprom.then(function(){
                        returnresult;
                    });
                }
                returnresult;
            },
        });

        assert.containsN(list,'.o_data_row',4,
            "shouldcontain4records");

        //clickonAddanddelaytheonchange(checkthatthebuttoniscorrectlydisabled)
        testUtils.dom.click(list.$buttons.find('.o_list_button_add'));
        assert.ok(list.$buttons.find('.o_list_button_add').get(0).disabled);

        prom.resolve();
        awaittestUtils.nextTick();

        assert.containsN(list,'.o_data_row',5,
            "onlyonerecordshouldhavebeencreated");

        list.destroy();
    });

    QUnit.test('referencefieldrendering',asyncfunction(assert){
        assert.expect(4);

        this.data.foo.records.push({
            id:5,
            reference:'res_currency,2',
        });

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<tree><fieldname="reference"/></tree>',
            mockRPC:function(route,args){
                if(args.method==='name_get'){
                    assert.step(args.model);
                }
                returnthis._super.apply(this,arguments);
            },
        });

        assert.verifySteps(['bar','res_currency'],"shouldhavedone1name_getbymodelinreferencevalues");
        assert.strictEqual(list.$('tbodytd:not(.o_list_record_selector)').text(),"Value1USDEUREUR",
            "shouldhavethedisplay_nameofthereference");
        list.destroy();
    });

    QUnit.test('referencefieldbatchedingroupedlist',asyncfunction(assert){
        assert.expect(8);

        this.data.foo.records=[
            //group1
            {id:1,foo:'1',reference:'bar,1'},
            {id:2,foo:'1',reference:'bar,2'},
            {id:3,foo:'1',reference:'res_currency,1'},
            //group2
            {id:4,foo:'2',reference:'bar,2'},
            {id:5,foo:'2',reference:'bar,3'},
        ];
        constlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:`<treeexpand="1">
                       <fieldname="foo"invisible="1"/>
                       <fieldname="reference"/>
                   </tree>`,
            groupBy:['foo'],
            mockRPC:function(route,args){
                assert.step(args.method||route);
                if(args.method==='name_get'){
                    if(args.model==='bar'){
                        assert.deepEqual(args.args[0],[1,2,3]);
                    }
                    if(args.model==="res_currency"){
                        assert.deepEqual(args.args[0],[1]);
                    }
                }
                returnthis._super.apply(this,arguments);
            },
        });
        assert.verifySteps([
            'web_read_group',
            'name_get',
            'name_get',
        ]);
        assert.containsN(list,'.o_group_header',2);
        constallNames=Array.from(list.el.querySelectorAll('.o_data_cell'),node=>node.textContent);
        assert.deepEqual(allNames,[
            'Value1',
            'Value2',
            'USD',
            'Value2',
            'Value3',
        ]);
        list.destroy();
    });

    QUnit.test('multieditinviewgroupedbyfieldnotinview',asyncfunction(assert){
        assert.expect(3);

        this.data.foo.records=[
            //group1
            {id:1,foo:'1',m2o:1},
            {id:3,foo:'2',m2o:1},
            //group2
            {id:2,foo:'1',m2o:2},
            {id:4,foo:'2',m2o:2},
            //group3
            {id:5,foo:'2',m2o:3},
        ];

        constlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:`<treeexpand="1"multi_edit="1">
                   <fieldname="foo"/>
               </tree>`,
            groupBy:['m2o'],
        });

        //Selectitemsfromthefirstgroup
        awaittestUtils.dom.click(list.$('.o_data_row.o_list_record_selectorinput:eq(0)'));
        awaittestUtils.dom.click(list.$('.o_data_row.o_list_record_selectorinput:eq(1)'));

        awaittestUtils.dom.click(list.$('.o_list_char:eq(0)'));

        awaittestUtils.fields.editInput(list.$('.o_field_widget[name=foo]'),'test');

        assert.containsOnce(document.body,'.modal');
        awaittestUtils.dom.click($('.modal.modal-footer.btn-primary'));
        assert.containsNone(document.body,'.modal');

        constallNames=[...document.querySelectorAll('.o_data_cell')].map(n=>n.textContent);
        assert.deepEqual(allNames,[
            'test',
            'test',
            '1',
            '2',
            '2',
        ]);

        list.destroy();
    });

    QUnit.test('multieditreferencefieldbatchedingroupedlist',asyncfunction(assert){
        assert.expect(18);

        this.data.foo.records=[
            //group1
            {id:1,foo:'1',reference:'bar,1'},
            {id:2,foo:'1',reference:'bar,2'},
            //group2
            {id:3,foo:'2',reference:'res_currency,1'},
            {id:4,foo:'2',reference:'bar,2'},
            {id:5,foo:'2',reference:'bar,3'},
        ];
        //Fieldboolean_togglejusttosimplifythetestflow
        letnameGetCount=0;
        constlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:`<treeexpand="1"multi_edit="1">
                       <fieldname="foo"invisible="1"/>
                       <fieldname="bar"widget="boolean_toggle"/>
                       <fieldname="reference"/>
                   </tree>`,
            groupBy:['foo'],
            mockRPC:function(route,args){
                assert.step(args.method||route);
                if(args.method==='write'){
                    assert.deepEqual(args.args,[[1,2,3],{bar:true}]);
                }
                if(args.method==='name_get'){
                    if(nameGetCount===2){
                        assert.strictEqual(args.model,'bar');
                        assert.deepEqual(args.args[0],[1,2]);
                    }
                    if(nameGetCount===3){
                        assert.strictEqual(args.model,'res_currency');
                        assert.deepEqual(args.args[0],[1]);
                    }
                    nameGetCount++;
                }
                returnthis._super.apply(this,arguments);
            },
        });

        assert.verifySteps([
            'web_read_group',
            'name_get',
            'name_get',
        ]);
        awaittestUtils.dom.click(list.$('.o_data_row.o_list_record_selectorinput')[0]);
        awaittestUtils.dom.click(list.$('.o_data_row.o_list_record_selectorinput')[1]);
        awaittestUtils.dom.click(list.$('.o_data_row.o_list_record_selectorinput')[2]);
        awaittestUtils.dom.click(list.$('.o_data_row.o_field_boolean')[0]);
        assert.containsOnce(document.body,'.modal');
        awaittestUtils.dom.click($('.modal.modal-footer.btn-primary'));
        assert.containsNone(document.body,'.modal');
        assert.verifySteps([
            'write',
            'read',
            'name_get',
            'name_get',
        ]);
        assert.containsN(list,'.o_group_header',2);

        constallNames=Array.from(list.el.querySelectorAll('.o_data_cell'))
            .filter(node=>!node.children.length).map(n=>n.textContent);
        assert.deepEqual(allNames,[
            'Value1',
            'Value2',
            'USD',
            'Value2',
            'Value3',
        ]);
        list.destroy();
    });

    QUnit.test('editablelistview:contextsarecorrectlysent',asyncfunction(assert){
        assert.expect(6);

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<treeeditable="top">'+
                        '<fieldname="foo"/>'+
                    '</tree>',
            mockRPC:function(route,args){
                varcontext;
                if(route==='/web/dataset/search_read'){
                    context=args.context;
                }else{
                    context=args.kwargs.context;
                }
                assert.strictEqual(context.active_field,2,"contextshouldbecorrect");
                assert.strictEqual(context.someKey,'somevalue',"contextshouldbecorrect");
                returnthis._super.apply(this,arguments);
            },
            session:{
                user_context:{someKey:'somevalue'},
            },
            viewOptions:{
                context:{active_field:2},
            },
        });

        awaittestUtils.dom.click(list.$('.o_data_cell:first'));
        awaittestUtils.fields.editInput(list.$('.o_field_widget[name=foo]'),'abc');
        awaittestUtils.dom.click(list.$buttons.find('.o_list_button_save'));

        list.destroy();
    });

    QUnit.test('editablelistview:contextswithmultipleedit',asyncfunction(assert){
        assert.expect(4);

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<treemulti_edit="1">'+
                        '<fieldname="foo"/>'+
                    '</tree>',
            mockRPC:function(route,args){
                if(route==='/web/dataset/call_kw/foo/write'||
                    route==='/web/dataset/call_kw/foo/read'){
                    varcontext=args.kwargs.context;
                    assert.strictEqual(context.active_field,2,"contextshouldbecorrect");
                    assert.strictEqual(context.someKey,'somevalue',"contextshouldbecorrect");
                }
                returnthis._super.apply(this,arguments);
            },
            session:{
                user_context:{someKey:'somevalue'},
            },
            viewOptions:{
                context:{active_field:2},
            },
        });

        //Usesthemainselectortoselectalllines.
        awaittestUtils.dom.click(list.$('.o_contentinput:first'));
        awaittestUtils.dom.click(list.$('.o_data_cell:first'));
        //Editsfirstrecordthenconfirmschanges.
        awaittestUtils.fields.editInput(list.$('.o_field_widget[name=foo]'),'legion');
        awaittestUtils.dom.click($('.modal-dialogbutton.btn-primary'));

        list.destroy();
    });

    QUnit.test('editablelistview:singleeditionwithselectedrecords',asyncfunction(assert){
        assert.expect(2);

        constlist=awaitcreateView({
            arch:`<treeeditable="top"multi_edit="1"><fieldname="foo"/></tree>`,
            data:this.data,
            model:'foo',
            View:ListView,
        });

        //Selectfirstrecord
        awaittestUtils.dom.click(list.$('.o_data_row:eq(0).o_list_record_selectorinput'));

        //Editthesecond
        awaittestUtils.dom.click(list.$('.o_data_row:eq(1).o_data_cell:first()'));
        awaittestUtils.fields.editInput(list.$('.o_data_row:eq(1).o_data_cell:first()input'),"oui");
        awaittestUtils.dom.click($('.o_list_button_save'));

        assert.strictEqual(list.$('.o_data_row:eq(0).o_data_cell:first()').text(),"yop",
            "Firstrowshouldremainunchanged");
        assert.strictEqual(list.$('.o_data_row:eq(1).o_data_cell:first()').text(),"oui",
            "Secondrowshouldhavebeenupdated");

        list.destroy();
    });

    QUnit.test('editablelistview:multiedition',asyncfunction(assert){
        assert.expect(26);

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<treeeditable="bottom"multi_edit="1">'+
                        '<fieldname="foo"/>'+
                        '<fieldname="int_field"/>'+
                    '</tree>',
            mockRPC:function(route,args){
                assert.step(args.method||route);
                if(args.method==='write'){
                    assert.deepEqual(args.args,[[1,2],{int_field:666}],
                        "shouldwriteonmultirecords");
                }elseif(args.method==='read'){
                    if(args.args[0].length!==1){
                        assert.deepEqual(args.args,[[1,2],['foo','int_field']],
                            "shouldbatchtheread");
                    }
                }
                returnthis._super.apply(this,arguments);
            },
        });

        assert.verifySteps(['/web/dataset/search_read']);

        //selecttworecords
        awaittestUtils.dom.click(list.$('.o_data_row:eq(0).o_list_record_selectorinput'));
        awaittestUtils.dom.click(list.$('.o_data_row:eq(1).o_list_record_selectorinput'));

        //editalinewitoutmodifyingafield
        awaittestUtils.dom.click(list.$('.o_data_row:eq(0).o_data_cell:eq(1)'));
        assert.hasClass(list.$('.o_data_row:eq(0)'),'o_selected_row',
            "thefirstrowshouldbeselected");
        awaittestUtils.dom.click('body');
        assert.containsNone(list,'.o_selected_row',"norowshouldbeselected");

        //createarecordandedititsvalue
        awaittestUtils.dom.click($('.o_list_button_add'));
        assert.verifySteps(['onchange']);

        awaittestUtils.fields.editInput(list.$('.o_selected_row.o_field_widget[name=int_field]'),123);
        assert.containsNone(document.body,'.modal',"themultieditionshouldnotbetriggeredduringcreation");

        awaittestUtils.dom.click($('.o_list_button_save'));
        assert.verifySteps(['create','read']);

        //editafield
        awaittestUtils.dom.click(list.$('.o_data_row:eq(0).o_data_cell:eq(1)'));
        awaittestUtils.fields.editInput(list.$('.o_field_widget[name=int_field]'),666);
        awaittestUtils.dom.click(list.$('.o_data_row:eq(0).o_data_cell:eq(0)'));
        assert.containsOnce(document.body,'.modal',"modalappearswhenswitchingcells");
        awaittestUtils.dom.click($('.modal.btn:contains(Cancel)'));
        assert.containsN(list,'.o_list_record_selectorinput:checked',2,
            "Selectionshouldremainunchanged");
        assert.strictEqual(list.$('.o_data_row:eq(0).o_data_cell').text(),'yop10',
            "changeshavebeendiscardedandrowisbacktoreadonly");
        assert.strictEqual(document.activeElement,list.$('.o_data_row:eq(0).o_data_cell:eq(1)')[0],
            "focusshouldbegiventothemostrecentlyeditedcellafterdiscard");
        awaittestUtils.dom.click(list.$('.o_data_row:eq(0).o_data_cell:eq(1)'));
        awaittestUtils.fields.editInput(list.$('.o_field_widget[name=int_field]'),666);
        awaittestUtils.dom.click(list.$('.o_data_row:eq(1).o_data_cell:eq(0)'));
        assert.ok($('.modal').text().includes('those2records'),"thenumberofrecordsshouldbecorrectlydisplayed");
        awaittestUtils.dom.click($('.modal.btn-primary'));
        assert.containsNone(list,'.o_data_cellinput.o_field_widget',"nofieldshouldbeeditableanymore");
        assert.containsNone(list,'.o_list_record_selectorinput:checked',"norecordshouldbeselectedanymore");
        assert.verifySteps(['write','read']);
        assert.strictEqual(list.$('.o_data_row:eq(0).o_data_cell').text(),"yop666",
            "thefirstrowshouldbeupdated");
        assert.strictEqual(list.$('.o_data_row:eq(1).o_data_cell').text(),"blip666",
            "thesecondrowshouldbeupdated");
        assert.containsNone(list,'.o_data_cellinput.o_field_widget',"nofieldshouldbeeditableanymore");
        assert.strictEqual(document.activeElement,list.$('.o_data_row:eq(0).o_data_cell:eq(1)')[0],
            "focusshouldbegiventothemostrecentlyeditedcellafterconfirm");

        list.destroy();
    });

    QUnit.test('createinmultieditablelist',asyncfunction(assert){
        assert.expect(1);

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<treemulti_edit="1">'+
                        '<fieldname="foo"/>'+
                        '<fieldname="int_field"/>'+
                    '</tree>',
            intercepts:{
                switch_view:function(ev){
                    assert.strictEqual(ev.data.view_type,'form');
                },
            },
        });

        //clickonCREATE(shouldtriggeraswitch_view)
        awaittestUtils.dom.click($('.o_list_button_add'));

        list.destroy();
    });

    QUnit.test('editablelistview:multieditioncannotcallonchanges',asyncfunction(assert){
        assert.expect(15);

        this.data.foo.onchanges={
            foo:function(obj){
                obj.int_field=obj.foo.length;
            },
        };
        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<treemulti_edit="1">'+
                        '<fieldname="foo"/>'+
                        '<fieldname="int_field"/>'+
                    '</tree>',
            mockRPC:function(route,args){
                assert.step(args.method||route);
                if(args.method==='write'){
                    args.args[1].int_field=args.args[1].foo.length;
                }
                returnthis._super.apply(this,arguments);
            },
        });

        assert.verifySteps(['/web/dataset/search_read']);

        //selectandeditasinglerecord
        awaittestUtils.dom.click(list.$('.o_data_row:eq(0).o_list_record_selectorinput'));
        awaittestUtils.dom.click(list.$('.o_data_row:eq(0).o_data_cell:eq(0)'));
        awaittestUtils.fields.editInput(list.$('.o_field_widget[name=foo]'),'hi');

        assert.containsNone(document.body,'.modal');
        assert.strictEqual(list.$('.o_data_row:eq(0).o_data_cell').text(),"hi2");
        assert.strictEqual(list.$('.o_data_row:eq(1).o_data_cell').text(),"blip9");

        assert.verifySteps(['write','read']);

        //selectthesecondrecord(thefirstoneisstillselected)
        assert.containsNone(list,'.o_list_record_selectorinput:checked');
        awaittestUtils.dom.click(list.$('.o_data_row:eq(0).o_list_record_selectorinput'));
        awaittestUtils.dom.click(list.$('.o_data_row:eq(1).o_list_record_selectorinput'));

        //editfoo,firstrow
        awaittestUtils.dom.click(list.$('.o_data_row:eq(0).o_data_cell:eq(0)'));
        awaittestUtils.fields.editInput(list.$('.o_field_widget[name=foo]'),'hello');
        awaittestUtils.dom.click(list.$('.o_data_row:eq(0).o_data_cell:eq(1)'));

        assert.containsOnce(document.body,'.modal');//savedialog
        awaittestUtils.dom.click($('.modal.btn-primary'));

        assert.strictEqual(list.$('.o_data_row:eq(0).o_data_cell').text(),"hello5");
        assert.strictEqual(list.$('.o_data_row:eq(1).o_data_cell').text(),"hello5");

        assert.verifySteps(['write','read'],"shouldnotperformtheonchangeinmultiedition");

        list.destroy();
    });

    QUnit.test('editablelistview:multieditionerrorandcancellationhandling',asyncfunction(assert){
        assert.expect(12);

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<treemulti_edit="1">'+
                        '<fieldname="foo"required="1"/>'+
                        '<fieldname="int_field"/>'+
                    '</tree>',
        });

        assert.containsN(list,'.o_list_record_selectorinput:enabled',5);

        //selecttworecords
        awaittestUtils.dom.click(list.$('.o_data_row:eq(0).o_list_record_selectorinput'));
        awaittestUtils.dom.click(list.$('.o_data_row:eq(1).o_list_record_selectorinput'));

        //editalineandcancel
        awaittestUtils.dom.click(list.$('.o_data_row:eq(0).o_data_cell:eq(0)'));
        assert.containsNone(list,'.o_list_record_selectorinput:enabled');
        awaittestUtils.fields.editInput(list.$('.o_selected_row.o_field_widget[name=foo]'),"abc");
        awaittestUtils.dom.click($('.modal.btn:contains("Cancel")'));
        assert.strictEqual(list.$('.o_data_row:eq(0).o_data_cell').text(),'yop10',"firstcellshouldhavediscardedanychange");
        assert.containsN(list,'.o_list_record_selectorinput:enabled',5);

        //editalinewithaninvalidformattype
        awaittestUtils.dom.click(list.$('.o_data_row:eq(0).o_data_cell:eq(1)'));
        assert.containsNone(list,'.o_list_record_selectorinput:enabled');
        awaittestUtils.fields.editInput(list.$('.o_selected_row.o_field_widget[name=int_field]'),"hahaha");
        assert.containsOnce(document.body,'.modal',"thereshouldbeanopenedmodal");
        awaittestUtils.dom.click($('.modal.btn-primary'));
        assert.strictEqual(list.$('.o_data_row:eq(0).o_data_cell').text(),'yop10',"changesshouldbediscarded");
        assert.containsN(list,'.o_list_record_selectorinput:enabled',5);

        //editalinewithaninvalidvalue
        awaittestUtils.dom.click(list.$('.o_data_row:eq(0).o_data_cell:eq(0)'));
        assert.containsNone(list,'.o_list_record_selectorinput:enabled');
        awaittestUtils.fields.editInput(list.$('.o_selected_row.o_field_widget[name=foo]'),"");
        assert.containsOnce(document.body,'.modal',"thereshouldbeanopenedmodal");
        awaittestUtils.dom.click($('.modal.btn-primary'));
        assert.strictEqual(list.$('.o_data_row:eq(0).o_data_cell').text(),'yop10',"changesshouldbediscarded");
        assert.containsN(list,'.o_list_record_selectorinput:enabled',5);

        list.destroy();
    });

    QUnit.test('multiedition:many2many_tagsinmany2manyfield',asyncfunction(assert){
        assert.expect(5);

        for(leti=4;i<=10;i++){
            this.data.bar.records.push({id:i,display_name:"Value"+i});
        }

        constlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<treemulti_edit="1"><fieldname="m2m"widget="many2many_tags"/></tree>',
            archs:{
                'bar,false,list':'<tree><fieldname="name"/></tree>',
                'bar,false,search':'<search></search>',
            },
        });

        assert.containsN(list,'.o_list_record_selectorinput:enabled',5);

        //selecttworecordsandentereditmode
        awaittestUtils.dom.click(list.$('.o_data_row:eq(0).o_list_record_selectorinput'));
        awaittestUtils.dom.click(list.$('.o_data_row:eq(1).o_list_record_selectorinput'));
        awaittestUtils.dom.click(list.$('.o_data_row:eq(0).o_data_cell'));

        awaittestUtils.fields.many2one.clickOpenDropdown("m2m");
        awaittestUtils.fields.many2one.clickItem("m2m","SearchMore");
        assert.containsOnce(document.body,'.modal.o_list_view',"shouldhaveopenthemodal");

        awaittestUtils.dom.click($('.modal.o_list_view.o_data_row:first'));

        assert.containsOnce(document.body,".modal[role='alert']","shouldhaveopentheconfirmationmodal");
        assert.containsN(document.body,".modal.o_field_many2manytags.badge",3);
        assert.strictEqual($(".modal.o_field_many2manytags.badge:last").text().trim(),"Value3",
            "shouldhavedisplay_nameinbadge");

        list.destroy();
    });

    QUnit.test('editablelistview:multieditionofmany2one:setsamevalue',asyncfunction(assert){
        assert.expect(4);

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<treemulti_edit="1">'+
                        '<fieldname="foo"/>'+
                        '<fieldname="m2o"/>'+
                    '</tree>',
            mockRPC:function(route,args){
                if(args.method==='write'){
                    assert.deepEqual(args.args,[[1,2,3,4],{m2o:1}],
                        "shouldforcewritevalueonallselectedrecords");
                }
                returnthis._super.apply(this,arguments);
            },
        });

        assert.strictEqual(list.$('.o_list_many2one').text(),"Value1Value2Value1Value1");

        //selectallrecords(thefirstonehasvalue1form2o)
        awaittestUtils.dom.click(list.$('thead.o_list_record_selectorinput'));

        //setm2oto1infirstrecord
        awaittestUtils.dom.click(list.$('.o_data_row:eq(0).o_data_cell:eq(1)'));
        awaittestUtils.fields.many2one.searchAndClickItem('m2o',{search:'Value1'});

        assert.containsOnce(document.body,'.modal');

        awaittestUtils.dom.click($('.modal.modal-footer.btn-primary'));

        assert.strictEqual(list.$('.o_list_many2one').text(),"Value1Value1Value1Value1");

        list.destroy();
    });

    QUnit.test('editablelistview:clickingon"Discardchanges"inmultiedition',asyncfunction(assert){
        assert.expect(2);

        constlist=awaitcreateView({
            arch:`
                <treeeditable="top"multi_edit="1">
                    <fieldname="foo"/>
                </tree>`,
            data:this.data,
            model:'foo',
            View:ListView,
        });

        //selecttworecords
        awaittestUtils.dom.click(list.$('.o_data_row:eq(0).o_list_record_selectorinput'));
        awaittestUtils.dom.click(list.$('.o_data_row:eq(1).o_list_record_selectorinput'));

        awaittestUtils.dom.click(list.$('.o_data_row:first().o_data_cell:first()'));
        list.$('.o_data_row:first().o_data_cell:first()input').val("oof");

        const$discardButton=list.$buttons.find('.o_list_button_discard');

        //Simulatesanactualclick(eventchainis:mousedown>change>blur>focus>mouseup>click)
        awaittestUtils.dom.triggerEvents($discardButton,['mousedown']);
        awaittestUtils.dom.triggerEvents(list.$('.o_data_row:first().o_data_cell:first()input'),
            ['change','blur','focusout']);
        awaittestUtils.dom.triggerEvents($discardButton,['focus']);
        $discardButton[0].dispatchEvent(newMouseEvent('mouseup'));
        awaittestUtils.dom.click($discardButton);

        assert.ok($('.modal').text().includes("Warning"),"Modalshouldasktodiscardchanges");
        awaittestUtils.dom.click($('.modal.btn-primary'));

        assert.strictEqual(list.$('.o_data_row:first().o_data_cell:first()').text(),"yop");

        list.destroy();
    });

    QUnit.test('editablelistview(multiedition):mousedownon"Discard",butmouseupsomewhereelse',asyncfunction(assert){
        assert.expect(1);

        constlist=awaitcreateView({
            arch:`
                <treemulti_edit="1">
                    <fieldname="foo"/>
                </tree>`,
            data:this.data,
            model:'foo',
            View:ListView,
        });

        //selecttworecords
        awaittestUtils.dom.click(list.$('.o_data_row:eq(0).o_list_record_selectorinput'));
        awaittestUtils.dom.click(list.$('.o_data_row:eq(1).o_list_record_selectorinput'));

        awaittestUtils.dom.click(list.$('.o_data_row:first().o_data_cell:first()'));
        list.$('.o_data_row:first().o_data_cell:first()input').val("oof");

        //Simulatesapseudodraganddrop
        awaittestUtils.dom.triggerEvents(list.$buttons.find('.o_list_button_discard'),['mousedown']);
        awaittestUtils.dom.triggerEvents(list.$('.o_data_row:first().o_data_cell:first()input'),
            ['change','blur','focusout']);
        awaittestUtils.dom.triggerEvents($(document.body),['focus']);
        window.dispatchEvent(newMouseEvent('mouseup'));
        awaittestUtils.nextTick();

        assert.ok($('.modal').text().includes("Confirmation"),"Modalshouldasktosavechanges");
        awaittestUtils.dom.click($('.modal.btn-primary'));

        list.destroy();
    });

    QUnit.test('editablelistview(multiedition):writablefieldsinreadonly(forcesave)',asyncfunction(assert){
        assert.expect(7);

        //booleantooglewidgetallowsforwritingontherecordeveninreadonlymode
        constlist=awaitcreateView({
            arch:`
                <treemulti_edit="1">
                    <fieldname="bar"widget="boolean_toggle"/>
                </tree>`,
            data:this.data,
            model:'foo',
            View:ListView,
            mockRPC(route,args){
                assert.step(args.method||route);
                if(args.method==='write'){
                    assert.deepEqual(args.args,[[1,3],{bar:false}]);
                }
                returnthis._super(...arguments);
            }
        });

        assert.verifySteps(['/web/dataset/search_read']);
        //selecttworecords
        awaittestUtils.dom.click(list.$('.o_data_row:eq(0).o_list_record_selectorinput'));
        awaittestUtils.dom.click(list.$('.o_data_row:eq(2).o_list_record_selectorinput'));

        awaittestUtils.dom.click(list.$('.o_data_row.o_field_boolean')[0]);

        assert.ok($('.modal').text().includes("Confirmation"),"Modalshouldasktosavechanges");
        awaittestUtils.dom.click($('.modal.btn-primary'));
        assert.verifySteps([
            'write',
            'read',
        ]);

        list.destroy();
    });

    QUnit.test('editablelistview:clickDiscard,CanceldiscarddialogandthenSaveinmultiedition',asyncfunction(assert){
        assert.expect(5);

        constlist=awaitcreateView({
            arch:`
                <treeeditable="top"multi_edit="1">
                    <fieldname="foo"/>
                </tree>`,
            data:this.data,
            model:'foo',
            View:ListView,
        });

        //selecttworecords
        awaittestUtils.dom.click(list.$('.o_data_row:eq(0).o_list_record_selectorinput'));
        awaittestUtils.dom.click(list.$('.o_data_row:eq(1).o_list_record_selectorinput'));

        awaittestUtils.dom.click(list.$('.o_data_row:first().o_data_cell:first()'));
        list.$('.o_data_row:first().o_data_cell:first()input').val("oof");

        const$discardButton=list.$buttons.find('.o_list_button_discard');

        //Simulatesanactualclick(eventchainis:mousedown>change>blur>focus>mouseup>click)
        awaittestUtils.dom.triggerEvents($discardButton,['mousedown']);
        awaittestUtils.dom.triggerEvents(list.$('.o_data_row:first().o_data_cell:first()input'),
            ['change','blur','focusout']);
        awaittestUtils.dom.triggerEvents($discardButton,['focus']);
        $discardButton[0].dispatchEvent(newMouseEvent('mouseup'));
        awaittestUtils.dom.click($discardButton);

        assert.ok($('.modal').text().includes("Warning"),"Modalshouldasktodiscardchanges");
        awaittestUtils.dom.click($('.modal.btn:contains(Cancel)'));
        assert.hasClass(list.$('.o_data_row:first'),'o_selected_row',
            "thefirstrowshouldstillbeselected");

        awaittestUtils.dom.click($('.o_list_button_save'));
        assert.containsOnce(document.body,'.modal');
        awaittestUtils.dom.click($('.modal.btn-primary'));
        assert.containsNone(list,'.o_selected_row');
        assert.strictEqual(list.$('.o_data_row.o_data_cell').text(),"oofoofgnapblip");

        list.destroy();
    });

    QUnit.test('editablelistview:multieditionwithreadonlymodifiers',asyncfunction(assert){
        assert.expect(5);

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<treemulti_edit="1">'+
                        '<fieldname="id"/>'+
                        '<fieldname="foo"/>'+
                        '<fieldname="int_field"attrs=\'{"readonly":[("id",">",2)]}\'/>'+
                    '</tree>',
            mockRPC:function(route,args){
                if(args.method==='write'){
                    assert.deepEqual(args.args,[[1,2],{int_field:666}],
                        "shouldonlywriteonthevalidrecords");
                }
                returnthis._super.apply(this,arguments);
            },
        });

        //selectallrecords
        awaittestUtils.dom.click(list.$('th.o_list_record_selectorinput'));

        //editafield
        awaittestUtils.dom.click(list.$('.o_data_row:eq(0).o_data_cell:eq(1)'));
        awaittestUtils.fields.editInput(list.$('.o_field_widget[name=int_field]'),666);

        constmodalText=$('.modal-body').text()
            .split("").filter(w=>w.trim()!=='').join("")
            .split("\n").join('');
        assert.strictEqual(modalText,
            "Amongthe4selectedrecords,2arevalidforthisupdate.Areyousureyouwantto"+
            "performthefollowingupdateonthose2records?Field:int_fieldUpdateto:666");
        assert.strictEqual(document.querySelector('.modal.o_modal_changes.o_field_widget').style.pointerEvents,'none',
            "pointereventsshouldbedeactivatedonthedemowidget");

        awaittestUtils.dom.click($('.modal.btn-primary'));
        assert.strictEqual(list.$('.o_data_row:eq(0).o_data_cell').text(),"1yop666",
            "thefirstrowshouldbeupdated");
        assert.strictEqual(list.$('.o_data_row:eq(1).o_data_cell').text(),"2blip666",
            "thesecondrowshouldbeupdated");
        list.destroy();
    });

    QUnit.test('editablelistview:multieditionwhenthedomainisselected',asyncfunction(assert){
        assert.expect(1);

        constlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:`
                <treemulti_edit="1"limit="2">
                    <fieldname="id"/>
                    <fieldname="int_field"/>
                </tree>`,
        });

        //selectallrecords,andthenselectalldomain
        awaittestUtils.dom.click(list.$('th.o_list_record_selectorinput'));
        awaittestUtils.dom.click(list.$('.o_list_selection_box.o_list_select_domain'));

        //editafield
        awaittestUtils.dom.click(list.$('.o_data_row:eq(0).o_data_cell:eq(1)'));
        awaittestUtils.fields.editInput(list.$('.o_field_widget[name=int_field]'),666);

        assert.ok($('.modal-body').text().includes('Thisupdatewillonlyconsidertherecordsofthecurrentpage.'));

        list.destroy();
    });

    QUnit.test('editablelistview:many2onewithreadonlymodifier',asyncfunction(assert){
        assert.expect(2);

        constlist=awaitcreateView({
            arch:
                `<treeeditable="top">
                    <fieldname="m2o"readonly="1"/>
                    <fieldname="foo"/>
                </tree>`,
            data:this.data,
            model:'foo',
            View:ListView,
        });

        //editafield
        awaittestUtils.dom.click(list.$('.o_data_row:eq(0).o_data_cell:eq(0)'));

        assert.containsOnce(list,'.o_data_row:eq(0).o_data_cell:eq(0)a[name="m2o"]');
        assert.strictEqual(document.activeElement,list.$('.o_data_row:eq(0).o_data_cell:eq(1)input')[0],
            "focusshouldgotothecharinput");

        list.destroy();
    });

    QUnit.test('editablelistview:multieditionservererrorhandling',asyncfunction(assert){
        assert.expect(3);

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<treemulti_edit="1">'+
                        '<fieldname="foo"required="1"/>'+
                    '</tree>',
            mockRPC:function(route,args){
                if(args.method==='write'){
                    returnPromise.reject();
                }
                returnthis._super.apply(this,arguments);
            },
        });

        //selecttworecords
        awaittestUtils.dom.click(list.$('.o_data_row:eq(0).o_list_record_selectorinput'));
        awaittestUtils.dom.click(list.$('.o_data_row:eq(1).o_list_record_selectorinput'));

        //editalineandconfirm
        awaittestUtils.dom.click(list.$('.o_data_row:eq(0).o_data_cell:eq(0)'));
        awaittestUtils.fields.editInput(list.$('.o_selected_row.o_field_widget[name=foo]'),"abc");
        awaittestUtils.dom.click('body');
        awaittestUtils.dom.click($('.modal.btn-primary'));
        //Servererror:iftherewasacrashmanager,therewouldbeanopenerroratthispoint...
        assert.strictEqual(list.$('.o_data_row:eq(0).o_data_cell').text(),'yop',
            "firstcellshouldhavediscardedanychange");
        assert.strictEqual(list.$('.o_data_row:eq(1).o_data_cell').text(),'blip',
            "secondselectedrecordshouldnothavechanged");
        assert.containsNone(list,'.o_data_cellinput.o_field_widget',
            "nofieldshouldbeeditableanymore");

        list.destroy();
    });

    QUnit.test('editablereadonlylistview:navigation',asyncfunction(assert){
        assert.expect(6);

        constlist=awaitcreateView({
            arch:`
                <treemulti_edit="1">
                    <fieldname="foo"/>
                    <fieldname="int_field"/>
                </tree>`,
            data:this.data,
            intercepts:{
                switch_view:function(event){
                    assert.strictEqual(event.data.res_id,3,
                        "'switch_view'eventhasbeentriggered");
                },
            },
            model:'foo',
            View:ListView,
        });

        //select2records
        awaittestUtils.dom.click(list.$('.o_data_row:eq(1).o_list_record_selectorinput'));
        awaittestUtils.dom.click(list.$('.o_data_row:eq(3).o_list_record_selectorinput'));

        //togglearowmode
        awaittestUtils.dom.click(list.$('.o_data_row:eq(1).o_data_cell:eq(1)'));
        assert.hasClass(list.$('.o_data_row:eq(1)'),'o_selected_row',
            "thesecondrowshouldbeselected");

        //Keyboardnavigationonlyinterractswithselectedelements
        awaittestUtils.fields.triggerKeydown(list.$('tr.o_selected_rowinput.o_field_widget[name="int_field"]'),'enter');
        assert.hasClass(list.$('.o_data_row:eq(3)'),'o_selected_row',
            "thefourthrowshouldbeselected");

        awaittestUtils.fields.triggerKeydown($(document.activeElement),'tab');
        awaittestUtils.fields.triggerKeydown($(document.activeElement),'tab');
        assert.hasClass(list.$('.o_data_row:eq(1)'),'o_selected_row',
            "thesecondrowshouldbeselectedagain");

        awaittestUtils.fields.triggerKeydown($(document.activeElement),'tab');
        awaittestUtils.fields.triggerKeydown($(document.activeElement),'tab');
        assert.hasClass(list.$('.o_data_row:eq(3)'),'o_selected_row',
            "thefourthrowshouldbeselectedagain");

        awaittestUtils.dom.click(list.$('.o_data_row:eq(2).o_data_cell:eq(0)'));
        assert.containsNone(list,'.o_data_cellinput.o_field_widget',
            "norowshouldbeeditableanymore");
        //Clickingonanunselectedrecordwhilenorowisbeingeditedwillopentherecord(switch_view)
        awaittestUtils.dom.click(list.$('.o_data_row:eq(2).o_data_cell:eq(0)'));

        awaittestUtils.dom.click(list.$('.o_data_row:eq(1).o_list_record_selectorinput'));
        awaittestUtils.dom.click(list.$('.o_data_row:eq(3).o_list_record_selectorinput'));

        list.destroy();
    });

    QUnit.test('editablelistview:multiedition:editandvalidatelastrow',asyncfunction(assert){
        assert.expect(3);

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<treemulti_edit="1">'+
                        '<fieldname="foo"/>'+
                        '<fieldname="int_field"/>'+
                    '</tree>',
            //inthistest,wewanttoaccuratelymockwhatreallyhappens,thatis,input
            //fieldsonlytriggertheirchangeson'change'event,noton'input'
            fieldDebounce:100000,
        });

        assert.containsN(list,'.o_data_row',4);

        //selectallrecords
        awaittestUtils.dom.click(list.$('.o_list_viewthead.o_list_record_selectorinput'));

        //editlastcelloflastline
        awaittestUtils.dom.click(list.$('.o_data_row:last.o_data_cell:last'));
        testUtils.fields.editInput(list.$('.o_field_widget[name=int_field]'),'666');
        awaittestUtils.fields.triggerKeydown(list.$('tr.o_selected_row.o_data_cell:lastinput'),'enter');

        assert.containsOnce(document.body,'.modal');
        awaittestUtils.dom.click($('.modal.btn-primary'));

        assert.containsN(list,'.o_data_row',4,
            "shouldnotcreateanewrowaswewereinmultiedition");

        list.destroy();
    });

    QUnit.test('editablereadonlylistview:navigationingroupedlist',asyncfunction(assert){
        assert.expect(6);

        constlist=awaitcreateView({
            arch:`
                <treemulti_edit="1">
                    <fieldname="foo"/>
                </tree>`,
            data:this.data,
            groupBy:['bar'],
            intercepts:{
                switch_view:function(event){
                    assert.strictEqual(event.data.res_id,3,
                        "'switch_view'eventhasbeentriggered");
                },
            },
            model:'foo',
            View:ListView,
        });

        //Openbothgroups
        awaittestUtils.dom.click(list.$('.o_group_header:first'));
        awaittestUtils.dom.click(list.$('.o_group_header:last'));

        //select2records
        awaittestUtils.dom.click(list.$('.o_data_row:eq(1).o_list_record_selectorinput'));
        awaittestUtils.dom.click(list.$('.o_data_row:eq(3).o_list_record_selectorinput'));

        //togglearowmode
        awaittestUtils.dom.click(list.$('.o_data_row:eq(1).o_data_cell:eq(0)'));
        assert.hasClass(list.$('.o_data_row:eq(1)'),'o_selected_row',
            "thesecondrowshouldbeselected");

        //Keyboardnavigationonlyinterractswithselectedelements
        awaittestUtils.fields.triggerKeydown(list.$('tr.o_selected_rowinput.o_field_widget'),'enter');
        assert.hasClass(list.$('.o_data_row:eq(3)'),'o_selected_row',
            "thefourthrowshouldbeselected");

        awaittestUtils.fields.triggerKeydown($(document.activeElement),'tab');
        assert.hasClass(list.$('.o_data_row:eq(1)'),'o_selected_row',
            "thesecondrowshouldbeselectedagain");

        awaittestUtils.fields.triggerKeydown($(document.activeElement),'tab');
        assert.hasClass(list.$('.o_data_row:eq(3)'),'o_selected_row',
            "thefourthrowshouldbeselectedagain");

        awaittestUtils.dom.click(list.$('.o_data_row:eq(2).o_data_cell:eq(0)'));
        assert.containsNone(list,'.o_data_cellinput.o_field_widget',"norowshouldbeeditableanymore");
        awaittestUtils.dom.click(list.$('.o_data_row:eq(2).o_data_cell:eq(0)'));

        list.destroy();
    });

    QUnit.test('editablereadonlylistview:singleeditiondoesnotbehavelikeamulti-edition',asyncfunction(assert){
        assert.expect(3);

        constlist=awaitcreateView({
            arch:`
                <treemulti_edit="1">
                    <fieldname="foo"required="1"/>
                </tree>`,
            data:this.data,
            model:'foo',
            View:ListView,
        });

        //selectarecord
        awaittestUtils.dom.click(list.$('.o_data_row:eq(0).o_list_record_selectorinput'));

        //editafield(invalidinput)
        awaittestUtils.dom.click(list.$('.o_data_row:eq(0).o_data_cell:eq(0)'));
        awaittestUtils.fields.editInput(list.$('.o_field_widget[name=foo]'),"");

        assert.containsOnce($('body'),'.modal',"shouldhaveamodal(invalidfields)");
        awaittestUtils.dom.click($('.modalbutton.btn'));

        //editafield
        awaittestUtils.dom.click(list.$('.o_data_row:eq(0).o_data_cell:eq(0)'));
        awaittestUtils.fields.editInput(list.$('.o_field_widget[name=foo]'),"bar");

        assert.containsNone($('body'),'.modal',"shouldnothaveamodal");
        assert.strictEqual(list.$('.o_data_row:eq(0).o_data_cell').text(),"bar",
            "thefirstrowshouldbeupdated");

        list.destroy();
    });

    QUnit.test('editablereadonlylistview:multiedition',asyncfunction(assert){
        assert.expect(14);

        constlist=awaitcreateView({
            arch:
                `<treemulti_edit="1">
                    <fieldname="foo"/>
                    <fieldname="int_field"required="1"/>
                </tree>`,
            data:this.data,
            mockRPC:function(route,args){
                assert.step(args.method||route);
                if(args.method==='write'){
                    assert.deepEqual(args.args,[[1,2],{int_field:0}],
                        "shouldwriteonmultirecords");
                }elseif(args.method==='read'){
                    if(args.args[0].length!==1){
                        assert.deepEqual(args.args,[[1,2],['foo','int_field']],
                            "shouldbatchtheread");
                    }
                }
                returnthis._super.apply(this,arguments);
            },
            model:'foo',
            View:ListView,
        });

        assert.verifySteps(['/web/dataset/search_read']);

        //selecttworecords
        awaittestUtils.dom.click(list.$('.o_data_row:eq(0).o_list_record_selectorinput'));
        awaittestUtils.dom.click(list.$('.o_data_row:eq(1).o_list_record_selectorinput'));

        //editafield
        awaittestUtils.dom.click(list.$('.o_data_row:eq(0).o_data_cell:eq(1)'));
        awaittestUtils.fields.editInput(list.$('.o_field_widget[name=int_field]'),666);
        awaittestUtils.dom.click(list.$('.o_data_row:eq(0).o_data_cell:eq(0)'));

        assert.containsOnce(document.body,'.modal',
            "modalappearswhenswitchingcells");

        awaittestUtils.dom.click($('.modal.btn:contains(Cancel)'));

        assert.strictEqual(list.$('.o_data_row:eq(0).o_data_cell').text(),'yop10',
            "changeshavebeendiscardedandrowisbacktoreadonly");

        awaittestUtils.dom.click(list.$('.o_data_row:eq(0).o_data_cell:eq(1)'));
        awaittestUtils.fields.editInput(list.$('.o_field_widget[name=int_field]'),0);
        awaittestUtils.dom.click(list.$('.o_data_row:eq(1).o_data_cell:eq(0)'));

        assert.containsOnce(document.body,'.modal',
            "thereshouldbeanopenedmodal");
        assert.ok($('.modal').text().includes('those2records'),
            "thenumberofrecordsshouldbecorrectlydisplayed");

        awaittestUtils.dom.click($('.modal.btn-primary'));

        assert.verifySteps(['write','read']);
        assert.strictEqual(list.$('.o_data_row:eq(0).o_data_cell').text(),"yop0",
            "thefirstrowshouldbeupdated");
        assert.strictEqual(list.$('.o_data_row:eq(1).o_data_cell').text(),"blip0",
            "thesecondrowshouldbeupdated");
        assert.containsNone(list,'.o_data_cellinput.o_field_widget',
            "nofieldshouldbeeditableanymore");

        list.destroy();
    });

    QUnit.test('editablelistview:m2mtagsingroupedlist',asyncfunction(assert){
        assert.expect(2);

        constlist=awaitcreateView({
            arch:`
                <treeeditable="top"multi_edit="1">
                    <fieldname="bar"/>
                    <fieldname="m2m"widget="many2many_tags"/>
                </tree>`,
            data:this.data,
            groupBy:['bar'],
            model:'foo',
            View:ListView,
        });

        //Opensfirstgroup
        awaittestUtils.dom.click(list.$('.o_group_header:first'));

        assert.notEqual(list.$('.o_data_row:first').text(),list.$('.o_data_row:last').text(),
            "Firstrowandlastrowshouldhavedifferentvalues");

        awaittestUtils.dom.click(list.$('thead.o_list_record_selector:firstinput'));
        awaittestUtils.dom.click(list.$('.o_data_row:first.o_data_cell:eq(1)'));
        awaittestUtils.dom.click(list.$('.o_selected_row.o_field_many2manytags.o_delete:first'));
        awaittestUtils.dom.click($('.modal.btn-primary'));

        assert.strictEqual(list.$('.o_data_row:first').text(),list.$('.o_data_row:last').text(),
            "Allrowsshouldhavebeencorrectlyupdated");

        list.destroy();
    });

    QUnit.test('editablelist:editmany2onefromexternallink',asyncfunction(assert){
        assert.expect(2);

        constlist=awaitcreateView({
            arch:`
                <treeeditable="top"multi_edit="1">
                    <fieldname="m2o"/>
                </tree>`,
            archs:{
                'bar,false,form':'<formstring="Bar"><fieldname="display_name"/></form>',
            },
            data:this.data,
            mockRPC:function(route,args){
                if(args.method==='get_formview_id'){
                    returnPromise.resolve(false);
                }
                returnthis._super(route,args);
            },
            model:'foo',
            View:ListView,
        });

        awaittestUtils.dom.click(list.$('thead.o_list_record_selector:firstinput'));
        awaittestUtils.dom.click(list.$('.o_data_row:first.o_data_cell:eq(0)'));
        awaittestUtils.dom.click(list.$('.o_external_button:first'));

        //ChangetheM2OvalueintheFormdialog
        awaittestUtils.fields.editInput($('.modalinput:first'),"OOF");
        awaittestUtils.dom.click($('.modal.btn-primary'));

        assert.strictEqual($('.modal.o_field_widget[name=m2o]').text(),"OOF",
            "Valueofthem2oshouldbeupdatedintheconfirmationdialog");

        //Closetheconfirmationdialog
        awaittestUtils.dom.click($('.modal.btn-primary'));

        assert.strictEqual(list.$('.o_data_cell:first').text(),"OOF",
            "Valueofthem2oshouldbeupdatedinthelist");

        list.destroy();
    });

    QUnit.test('editablelistwithfieldswithreadonlymodifier',asyncfunction(assert){
        assert.expect(8);

        constlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:`
                <treeeditable="top">
                    <fieldname="bar"/>
                    <fieldname="foo"attrs="{'readonly':[['bar','=',True]]}"/>
                    <fieldname="m2o"attrs="{'readonly':[['bar','=',False]]}"/>
                    <fieldname="int_field"/>
                </tree>`,
        });

        awaittestUtils.dom.click(list.$('.o_list_button_add'));

        assert.containsOnce(list,'.o_selected_row');
        assert.notOk(list.$('.o_selected_row.o_field_booleaninput').is(':checked'));
        assert.doesNotHaveClass(list.$('.o_selected_row.o_list_char'),'o_readonly_modifier');
        assert.hasClass(list.$('.o_selected_row.o_list_many2one'),'o_readonly_modifier');

        awaittestUtils.dom.click(list.$('.o_selected_row.o_field_booleaninput'));

        assert.ok(list.$('.o_selected_row.o_field_booleaninput').is(':checked'));
        assert.hasClass(list.$('.o_selected_row.o_list_char'),'o_readonly_modifier');
        assert.doesNotHaveClass(list.$('.o_selected_row.o_list_many2one'),'o_readonly_modifier');

        awaittestUtils.dom.click(list.$('.o_selected_row.o_field_many2oneinput'));

        assert.strictEqual(document.activeElement,list.$('.o_selected_row.o_field_many2oneinput')[0]);

        list.destroy();
    });

    QUnit.test('editablelistwithmany2one:clickoutdoesnotdiscardtherow',asyncfunction(assert){
        //Inthistest,wesimulatealongclickbymanuallytriggeringamousedownandlateron
        //mouseupandclickevents
        assert.expect(5);

        this.data.bar.fields.m2o={string:"M2Ofield",type:"many2one",relation:"foo"};

        constform=awaitcreateView({
            View:FormView,
            model:'foo',
            data:this.data,
            arch:`
                <form>
                    <fieldname="display_name"/>
                    <fieldname="o2m">
                        <treeeditable="bottom">
                            <fieldname="m2o"required="1"/>
                        </tree>
                    </field>
                </form>`,
        });

        assert.containsNone(form,'.o_data_row');

        awaittestUtils.dom.click(form.$('.o_field_x2many_list_row_add>a'));
        assert.containsOnce(form,'.o_data_row');

        //focusandwritesomethinginthem2o
        form.$('.o_field_many2oneinput').focus().val('abcdef').trigger('keyup');
        awaittestUtils.nextTick();

        //thensimulateamousedownoutside
        form.$('.o_field_widget[name="display_name"]').focus().trigger('mousedown');
        awaittestUtils.nextTick();
        assert.containsOnce(document.body,'.modal',"shouldaskconfirmationtocreatearecord");

        //triggerthemouseupandtheclick
        form.$('.o_field_widget[name="display_name"]').trigger('mouseup').trigger('click');
        awaittestUtils.nextTick();

        assert.containsOnce(document.body,'.modal',"modalshouldstillbedisplayed");
        assert.containsOnce(form,'.o_data_row',"therowshouldstillbethere");

        form.destroy();
    });

    QUnit.test('editablelistalongsidehtmlfield:clickouttounselecttherow',asyncfunction(assert){
        assert.expect(5);

        constform=awaitcreateView({
            View:FormView,
            model:'foo',
            data:this.data,
            arch:`
                <form>
                    <fieldname="text"widget="html"/>
                    <fieldname="o2m">
                        <treeeditable="bottom">
                            <fieldname="display_name"/>
                        </tree>
                    </field>
                </form>`,
        });

        assert.containsNone(form,'.o_data_row');

        awaittestUtils.dom.click(form.$('.o_field_x2many_list_row_add>a'));
        assert.containsOnce(form,'.o_data_row');
        assert.hasClass(form.$('.o_data_row'),'o_selected_row');

        //clickoutsidetounselecttherow
        awaittestUtils.dom.click(document.body);
        assert.containsOnce(form,'.o_data_row');
        assert.doesNotHaveClass(form.$('.o_data_row'),'o_selected_row');

        form.destroy();
    });

    QUnit.test('listgroupedbydate:month',asyncfunction(assert){
        assert.expect(1);

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<tree><fieldname="date"/></tree>',
            groupBy:['date:month'],
        });

        assert.strictEqual(list.$('tbody').text(),"January2017(1)Undefined(3)",
            "thegroupnamesshouldbecorrect");

        list.destroy();
    });

    QUnit.test('groupedlisteditionwithtoggle_buttonwidget',asyncfunction(assert){
        assert.expect(3);

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<tree><fieldname="bar"widget="toggle_button"/></tree>',
            groupBy:['m2o'],
            mockRPC:function(route,args){
                if(args.method==='write'){
                    assert.deepEqual(args.args[1],{bar:false},
                        "shouldwritethecorrectvalue");
                }
                returnthis._super.apply(this,arguments);
            },
        });

        awaittestUtils.dom.click(list.$('.o_group_header:first'));
        assert.containsOnce(list,'.o_data_row:first.o_toggle_button_success',
            "booleanvalueofthefirstrecordshouldbetrue");
        awaittestUtils.dom.click(list.$('.o_data_row:first.o_icon_button'));
        assert.strictEqual(list.$('.o_data_row:first.text-muted:not(.o_toggle_button_success)').length,1,
            "booleanbuttonshouldhavebeenupdated");

        list.destroy();
    });

    QUnit.test('groupedlistview,indentationforemptygroup',asyncfunction(assert){
        assert.expect(3);

        this.data.foo.fields.priority={
            string:"Priority",
            type:"selection",
            selection:[[1,"Low"],[2,"Medium"],[3,"High"]],
            default:1,
        };
        this.data.foo.records.push({id:5,foo:"blip",int_field:-7,m2o:1,priority:2});
        this.data.foo.records.push({id:6,foo:"blip",int_field:5,m2o:1,priority:3});

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<tree><fieldname="id"/></tree>',
            groupBy:['priority','m2o'],
            mockRPC:function(route,args){
                //Overrideoftheread_grouptodisplaytherowevenifthereisnorecordinit,
                //tomockthebehavihourofsomefieldse.gstage_idonthesaleorder.
                if(args.method==='web_read_group'&&args.kwargs.groupby[0]==="m2o"){
                    returnPromise.resolve({
                        groups:[{
                            id:8,
                            m2o:[1,"Value1"],
                            m2o_count:0
                        },{
                            id:2,
                            m2o:[2,"Value2"],
                            m2o_count:1
                        }],
                        length:1,
                    });
                }
                returnthis._super.apply(this,arguments);
            },
        });

        //openthefirstgroup
        awaittestUtils.dom.click(list.$('.o_group_header:first'));
        assert.strictEqual(list.$('th.o_group_name').eq(1).children().length,1,
            "Thereshouldbeanemptyelementcreatingtheindentationforthesubgroup.");
        assert.hasClass(list.$('th.o_group_name').eq(1).children().eq(0),'fa',
            "Thefirstelementoftherownameshouldhavethefaclass");
        assert.strictEqual(list.$('th.o_group_name').eq(1).children().eq(0).is('span'),true,
            "Thefirstelementoftherownameshouldbeaspan");
        list.destroy();
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

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<tree><fieldname="foo"/><fieldname="int_field"/><widgetname="test"/></tree>',
        });

        assert.strictEqual(list.$('.o_widget').first().text(),'{"foo":"yop","int_field":10,"id":1}',
            "widgetshouldhavebeeninstantiated");

        list.destroy();
        deletewidgetRegistry.map.test;
    });

    QUnit.test('usethelimitattributeinarch',asyncfunction(assert){
        assert.expect(4);

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<treelimit="2"><fieldname="foo"/></tree>',
            mockRPC:function(route,args){
                assert.strictEqual(args.limit,2,
                    'shouldusethecorrectlimitvalue');
                returnthis._super.apply(this,arguments);
            },
        });


        assert.strictEqual(cpHelpers.getPagerValue(list),'1-2');
        assert.strictEqual(cpHelpers.getPagerSize(list),'4');

        assert.containsN(list,'.o_data_row',2,
            'shoulddisplay2datarows');
        list.destroy();
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
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<treestring="Partners">'+
                    '<fieldname="foo"/>'+
                    '<fieldname="bar"/>'+
                    '<fieldname="date"/>'+
                    '<fieldname="int_field"/>'+
                    '<fieldname="qux"/>'+
                    '<fieldname="m2o"/>'+
                    '<fieldname="o2m"/>'+
                    '<fieldname="m2m"/>'+
                    '<fieldname="amount"/>'+
                    '<fieldname="currency_id"/>'+
                    '<fieldname="datetime"/>'+
                    '<fieldname="reference"/>'+
                '</tree>',
        };

        varlist=awaitcreateView(params);
        assert.ok(instanceNumber>0);

        list.destroy();
        assert.strictEqual(instanceNumber,0);

        testUtils.mock.unpatch(mixins.ParentedMixin);
    });

    QUnit.test('concurrentreloadsfinishingininverseorder',asyncfunction(assert){
        assert.expect(4);

        varblockSearchRead=false;
        varprom=testUtils.makeTestPromise();
        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<tree><fieldname="foo"/></tree>',
            mockRPC:function(route){
                varresult=this._super.apply(this,arguments);
                if(route==='/web/dataset/search_read'&&blockSearchRead){
                    returnprom.then(_.constant(result));
                }
                returnresult;
            },
        });

        assert.containsN(list,'.o_list_view.o_data_row',4,
            "listviewshouldcontain4records");

        //reloadwithadomain(thisrequestisblocked)
        blockSearchRead=true;
        list.reload({domain:[['foo','=','yop']]});
        awaittestUtils.nextTick();

        assert.containsN(list,'.o_list_view.o_data_row',4,
            "listviewshouldstillcontain4records(search_readbeingblocked)");

        //reloadwithoutthedomain
        blockSearchRead=false;
        list.reload({domain:[]});
        awaittestUtils.nextTick();

        assert.containsN(list,'.o_list_view.o_data_row',4,
            "listviewshouldstillcontain4records");

        //unblocktheRPC
        prom.resolve();
        awaittestUtils.nextTick();

        assert.containsN(list,'.o_list_view.o_data_row',4,
            "listviewshouldstillcontain4records");

        list.destroy();
    });

    QUnit.test('listviewona"noCache"model',asyncfunction(assert){
        assert.expect(9);

        testUtils.mock.patch(BasicModel,{
            noCacheModels:BasicModel.prototype.noCacheModels.concat(['foo']),
        });

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<treeeditable="top">'+
                    '<fieldname="display_name"/>'+
                '</tree>',
            mockRPC:function(route,args){
                if(_.contains(['create','unlink','write'],args.method)){
                    assert.step(args.method);
                }
                returnthis._super.apply(this,arguments);
            },
            viewOptions:{
                hasActionMenus:true,
            },
        });
        core.bus.on('clear_cache',list,assert.step.bind(assert,'clear_cache'));

        //createanewrecord
        awaittestUtils.dom.click(list.$buttons.find('.o_list_button_add'));
        awaittestUtils.fields.editInput(list.$('.o_selected_row.o_field_widget'),'somevalue');
        awaittestUtils.dom.click(list.$buttons.find('.o_list_button_save'));

        //editanexistingrecord
        awaittestUtils.dom.click(list.$('.o_data_cell:first'));
        awaittestUtils.fields.editInput(list.$('.o_selected_row.o_field_widget'),'newvalue');
        awaittestUtils.dom.click(list.$buttons.find('.o_list_button_save'));

        //deletearecord
        awaittestUtils.dom.click(list.$('.o_data_row:first.o_list_record_selectorinput'));
        awaitcpHelpers.toggleActionMenu(list);
        awaitcpHelpers.toggleMenuItem(list,"Delete");
        awaittestUtils.dom.click($('.modal-footer.btn-primary'));

        assert.verifySteps([
            'create',
            'clear_cache',
            'write',
            'clear_cache',
            'unlink',
            'clear_cache',
        ]);

        list.destroy();
        testUtils.mock.unpatch(BasicModel);

        assert.verifySteps(['clear_cache']);//triggeredbythetestenvironmentondestroy
    });

    QUnit.test('listviewmovetopreviouspagewhenallrecordsfromlastpagedeleted',asyncfunction(assert){
        assert.expect(5);

        letcheckSearchRead=false;
        constlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<treelimit="3">'+
                '<fieldname="display_name"/>'+
                '</tree>',
            mockRPC:function(route,args){
                if(checkSearchRead&&route==='/web/dataset/search_read'){
                    assert.strictEqual(args.limit,3,"limitshould3");
                    assert.notOk(args.offset,"offsetshouldnotbepassedi.e.offset0bydefault");
                }
                returnthis._super.apply(this,arguments);
            },
            viewOptions:{
                hasActionMenus:true,
            },
        });

        assert.strictEqual(list.$('.o_pager_counter').text().trim(),'1-3/4',
        "shouldhave2pagesandcurrentpageshouldbefirstpage");

        //movetonextpage
        awaittestUtils.dom.click(list.$('.o_pager_next'));
        assert.strictEqual(list.$('.o_pager_counter').text().trim(),'4-4/4',
        "shouldbeonsecondpage");

        //deletearecord
        awaittestUtils.dom.click(list.$('tbody.o_data_row:firsttd.o_list_record_selector:firstinput'));
        checkSearchRead=true;
        awaittestUtils.dom.click(list.$('.o_dropdown_toggler_btn:contains(Action)'));
        awaittestUtils.dom.click(list.$('a:contains(Delete)'));
        awaittestUtils.dom.click($('body.modalbuttonspan:contains(Ok)'));
        assert.strictEqual(list.$('.o_pager_counter').text().trim(),'1-3/3',
            "shouldhave1pageonly");

        list.destroy();
    });

    QUnit.test('groupedlistviewmovetopreviouspageofgroupwhenallrecordsfromlastpagedeleted',asyncfunction(assert){
        assert.expect(7);

        letcheckSearchRead=false;
        constlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<treelimit="2">'+
                '<fieldname="display_name"/>'+
                '</tree>',
            mockRPC:function(route,args){
                if(checkSearchRead&&route==='/web/dataset/search_read'){
                    assert.strictEqual(args.limit,2,"limitshould2");
                    assert.notOk(args.offset,"offsetshouldnotbepassedi.e.offset0bydefault");
                }
                returnthis._super.apply(this,arguments);
            },
            viewOptions:{
                hasActionMenus:true,
            },
            groupBy:['m2o'],
        });

        assert.strictEqual(list.$('th:contains(Value1(3))').length,1,
            "Value1shouldcontain3records");
        assert.strictEqual(list.$('th:contains(Value2(1))').length,1,
            "Value2shouldcontain1record");

        awaittestUtils.dom.click(list.$('th.o_group_name:nth(0)'));
        assert.strictEqual(list.$('th.o_group_name:eq(0).o_pager_counter').text().trim(),'1-2/3',
            "shouldhave2pagesandcurrentpageshouldbefirstpage");

        //movetonextpage
        awaittestUtils.dom.click(list.$('.o_group_header.o_pager_next'));
        assert.strictEqual(list.$('th.o_group_name:eq(0).o_pager_counter').text().trim(),'3-3/3',
            "shouldbeonsecondpage");

        //deletearecord
        awaittestUtils.dom.click(list.$('tbody.o_data_row:firsttd.o_list_record_selector:firstinput'));
        checkSearchRead=true;
        awaittestUtils.dom.click(list.$('.o_dropdown_toggler_btn:contains(Action)'));
        awaittestUtils.dom.click(list.$('a:contains(Delete)'));
        awaittestUtils.dom.click($('body.modalbuttonspan:contains(Ok)'));

        assert.strictEqual(list.$('th.o_group_name:eq(0).o_pager_counter').text().trim(),'',
            "shouldbeonfirstpagenow");

        list.destroy();
    });

    QUnit.test('listviewmovetopreviouspagewhenallrecordsfromlastpagearchive/unarchived',asyncfunction(assert){
        assert.expect(9);

        //addactivefieldonfoomodelandmakeallrecordsactive
        this.data.foo.fields.active={string:'Active',type:'boolean',default:true};

        constlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<treelimit="3"><fieldname="display_name"/></tree>',
            viewOptions:{
                hasActionMenus:true,
            },
            mockRPC:function(route){
                if(route==='/web/dataset/call_kw/foo/action_archive'){
                    this.data.foo.records[3].active=false;
                    returnPromise.resolve();
                }
                returnthis._super.apply(this,arguments);
            },
        });

        assert.strictEqual(list.$('.o_pager_counter').text().trim(),'1-3/4',
            "shouldhave2pagesandcurrentpageshouldbefirstpage");
        assert.strictEqual(list.$('tbodytd.o_list_record_selector').length,3,
            "shouldhave3records");

        //movetonextpage
        awaittestUtils.dom.click(list.$('.o_pager_next'));
        assert.strictEqual(list.$('.o_pager_counter').text().trim(),'4-4/4',
            "shouldbeonsecondpage");
        assert.strictEqual(list.$('tbodytd.o_list_record_selector').length,1,
            "shouldhave1records");
        assert.containsNone(list,'.o_cp_action_menus','sidebarshouldnotbeavailable');

        awaittestUtils.dom.click(list.$('tbody.o_data_row:firsttd.o_list_record_selector:firstinput'));
        assert.containsOnce(list,'.o_cp_action_menus','sidebarshouldbeavailable');

        //archiveallrecordsofcurrentpage
        awaittestUtils.dom.click(list.$('.o_cp_action_menus.o_dropdown_toggler_btn:contains(Action)'));
        awaittestUtils.dom.click(list.$('a:contains(Archive)'));
        assert.strictEqual($('.modal').length,1,'aconfirmmodalshouldbedisplayed');

        awaittestUtils.dom.click($('body.modalbuttonspan:contains(Ok)'));
        assert.strictEqual(list.$('tbodytd.o_list_record_selector').length,3,
            "shouldhave3records");
        assert.strictEqual(list.$('.o_pager_counter').text().trim(),'1-3/3',
            "shouldhave1pageonly");

        list.destroy();
    });

    QUnit.test('listshouldasktoscrolltotoponpagechanges',asyncfunction(assert){
        assert.expect(10);

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<treelimit="3">'+
                    '<fieldname="display_name"/>'+
                '</tree>',
            intercepts:{
                scrollTo:function(ev){
                    assert.strictEqual(ev.data.top,0,
                        "shouldasktoscrolltotop");
                    assert.step('scroll');
                },
            },
        });


        //switchpages(shouldasktoscroll)
        awaitcpHelpers.pagerNext(list);
        awaitcpHelpers.pagerPrevious(list);
        assert.verifySteps(['scroll','scroll'],
            "shouldasktoscrollwhenswitchingpages");

        //changethelimit(shouldnotasktoscroll)
        awaitcpHelpers.setPagerValue(list,'1-2');
        awaittestUtils.nextTick();
        assert.strictEqual(cpHelpers.getPagerValue(list),'1-2');
        assert.verifySteps([],"shouldnotasktoscrollwhenchangingthelimit");

        //switchpagesagain(shouldstillasktoscroll)
        awaitcpHelpers.pagerNext(list);

        assert.verifySteps(['scroll'],"thisisstillworkingafteralimitchange");

        list.destroy();
    });

    QUnit.test('listwithhandlefield,overridedefault_get,bottomwheninline',asyncfunction(assert){
        assert.expect(2);

        this.data.foo.fields.int_field.default=10;

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:
                '<treeeditable="bottom"default_order="int_field">'
                    +'<fieldname="int_field"widget="handle"/>'
                    +'<fieldname="foo"/>'
                +'</tree>',
        });

        //startingcondition
        assert.strictEqual($('.o_data_cell').text(),"blipblipyopgnap");

        //clickaddanewline
        //savetherecord
        //checklineisatthecorrectplace

        varinputText='ninja';
        awaittestUtils.dom.click($('.o_list_button_add'));
        awaittestUtils.fields.editInput(list.$('.o_input[name="foo"]'),inputText);
        awaittestUtils.dom.click($('.o_list_button_save'));
        awaittestUtils.dom.click($('.o_list_button_add'));

        assert.strictEqual($('.o_data_cell').text(),"blipblipyopgnap"+inputText);

        list.destroy();
    });

    QUnit.test('createrecordonlistwithmodifiersdependingonid',asyncfunction(assert){
        assert.expect(8);

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<treeeditable="top">'+
                    '<fieldname="id"invisible="1"/>'+
                    '<fieldname="foo"attrs="{\'readonly\':[[\'id\',\'!=\',False]]}"/>'+
                    '<fieldname="int_field"attrs="{\'invisible\':[[\'id\',\'!=\',False]]}"/>'+
                '</tree>',
        });

        //addanewrecord
        awaittestUtils.dom.click(list.$buttons.find('.o_list_button_add'));

        //modifiersshouldbeevalutedtofalse
        assert.containsOnce(list,'.o_selected_row');
        assert.doesNotHaveClass(list.$('.o_selected_row.o_data_cell:first'),'o_readonly_modifier');
        assert.doesNotHaveClass(list.$('.o_selected_row.o_data_cell:nth(1)'),'o_invisible_modifier');

        //setavalueandsave
        awaittestUtils.fields.editInput(list.$('.o_selected_rowinput[name=foo]'),'somevalue');
        awaittestUtils.dom.click(list.$buttons.find('.o_list_button_save'));

        //modifiersshouldbeevalutedtotrue
        assert.hasClass(list.$('.o_data_row:first.o_data_cell:first'),'o_readonly_modifier');
        assert.hasClass(list.$('.o_data_row:first.o_data_cell:nth(1)'),'o_invisible_modifier');

        //editagainthejustcreatedrecord
        awaittestUtils.dom.click(list.$('.o_data_row:first.o_data_cell:first'));

        //modifiersshouldbeevalutedtotrue
        assert.containsOnce(list,'.o_selected_row');
        assert.hasClass(list.$('.o_selected_row.o_data_cell:first'),'o_readonly_modifier');
        assert.hasClass(list.$('.o_selected_row.o_data_cell:nth(1)'),'o_invisible_modifier');

        list.destroy();
    });

    QUnit.test('readonlybooleanineditablelistisreadonly',asyncfunction(assert){
        assert.expect(6);

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<treeeditable="bottom">'+
                      '<fieldname="foo"/>'+
                      '<fieldname="bar"attrs="{\'readonly\':[(\'foo\',\'!=\',\'yop\')]}"/>'+
                  '</tree>',
        });

        //clickingondisabledcheckboxwithactiverowdoesnotwork
        var$disabledCell=list.$('.o_data_row:eq(1).o_data_cell:last-child');
        awaittestUtils.dom.click($disabledCell.prev());
        assert.containsOnce($disabledCell,':disabled:checked');
        var$disabledLabel=$disabledCell.find('.custom-control-label');
        awaittestUtils.dom.click($disabledLabel);
        assert.containsOnce($disabledCell,':checked',
            "clickingdisabledcheckboxdidnotwork"
        );
        assert.ok(
            $(document.activeElement).is('input[type="text"]'),
            "disabledcheckboxisnotfocusedafterclick"
        );

        //clickingonenabledcheckboxwithactiverowtogglescheckmark
        var$enabledCell=list.$('.o_data_row:eq(0).o_data_cell:last-child');
        awaittestUtils.dom.click($enabledCell.prev());
        assert.containsOnce($enabledCell,':checked:not(:disabled)');
        var$enabledLabel=$enabledCell.find('.custom-control-label');
        awaittestUtils.dom.click($enabledLabel);
        assert.containsNone($enabledCell,':checked',
            "clickingenabledcheckboxworkedanduncheckedit"
        );
        assert.ok(
            $(document.activeElement).is('input[type="checkbox"]'),
            "enabledcheckboxisfocusedafterclick"
        );

        list.destroy();
    });

    QUnit.test('groupedlistwithasyncwidget',asyncfunction(assert){
        assert.expect(4);

        varprom=testUtils.makeTestPromise();
        varAsyncWidget=Widget.extend({
            willStart:function(){
                returnprom;
            },
            start:function(){
                this.$el.text('ready');
            },
        });
        widgetRegistry.add('asyncWidget',AsyncWidget);

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<tree><widgetname="asyncWidget"/></tree>',
            groupBy:['int_field'],
        });

        assert.containsNone(list,'.o_data_row',"nogroupshouldbeopen");

        awaittestUtils.dom.click(list.$('.o_group_header:first'));

        assert.containsNone(list,'.o_data_row',
            "shouldwaitforasyncwidgetsbeforeopeningthegroup");

        prom.resolve();
        awaittestUtils.nextTick();

        assert.containsN(list,'.o_data_row',1,"groupshouldbeopen");
        assert.strictEqual(list.$('.o_data_row.o_data_cell').text(),'ready',
            "asyncwidgetshouldbecorrectlydisplayed");

        list.destroy();
        deletewidgetRegistry.map.asyncWidget;
    });

    QUnit.test('groupedlistswithgroups_limitattribute',asyncfunction(assert){
        assert.expect(8);

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<treegroups_limit="3"><fieldname="foo"/></tree>',
            groupBy:['int_field'],
            mockRPC:function(route,args){
                assert.step(args.method||route);
                returnthis._super.apply(this,arguments);
            },
        });

        assert.containsN(list,'.o_group_header',3);//page1
        assert.containsNone(list,'.o_data_row');
        assert.containsOnce(list,'.o_pager');//hasapager

        awaitcpHelpers.pagerNext(list);//switchtopage2

        assert.containsN(list,'.o_group_header',1);//page2
        assert.containsNone(list,'.o_data_row');

        assert.verifySteps([
            'web_read_group',//read_grouppage1
            'web_read_group',//read_grouppage2
        ]);

        list.destroy();
    });

    QUnit.test('groupedlistwithexpandattribute',asyncfunction(assert){
        assert.expect(5);

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<treeexpand="1"><fieldname="foo"/></tree>',
            groupBy:['bar'],
            mockRPC:function(route,args){
                assert.step(args.method||route);
                returnthis._super.apply(this,arguments);
            }
        });

        assert.containsN(list,'.o_group_header',2);
        assert.containsN(list,'.o_data_row',4);
        assert.strictEqual(list.$('.o_data_cell').text(),'yopblipgnapblip');

        assert.verifySteps([
            'web_read_group',//recordsarefetchedalongsidegroups
        ]);

        list.destroy();
    });

    QUnit.test('groupedlist(twolevels)withexpandattribute',asyncfunction(assert){
        //theexpandattributeonlyopensthefirstlevelgroups
        assert.expect(5);

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<treeexpand="1"><fieldname="foo"/></tree>',
            groupBy:['bar','int_field'],
            mockRPC:function(route,args){
                assert.step(args.method||route);
                returnthis._super.apply(this,arguments);
            }
        });

        assert.containsN(list,'.o_group_header',6);

        assert.verifySteps([
            'web_read_group',//global
            'web_read_group',//firstgroup
            'web_read_group',//secondgroup
        ]);

        list.destroy();
    });

    QUnit.test('groupedlistswithexpandattributeandalotofgroups',asyncfunction(assert){
        assert.expect(8);

        for(vari=0;i<15;i++){
            this.data.foo.records.push({foo:'record'+i,int_field:i});
        }

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<treeexpand="1"><fieldname="foo"/></tree>',
            groupBy:['int_field'],
            mockRPC:function(route,args){
                if(args.method==='web_read_group'){
                    assert.step(args.method);
                }
                returnthis._super.apply(this,arguments);
            },
        });

        assert.containsN(list,'.o_group_header',10);//page1
        assert.containsN(list,'.o_data_row',11);//onegroupcontainstworecords
        assert.containsOnce(list,'.o_pager');//hasapager

        awaitcpHelpers.pagerNext(list);//switchtopage2

        assert.containsN(list,'.o_group_header',7);//page2
        assert.containsN(list,'.o_data_row',7);

        assert.verifySteps([
            'web_read_group',//read_grouppage1
            'web_read_group',//read_grouppage2
        ]);

        list.destroy();
    });

    QUnit.test('addfilterinagroupedlistwithapager',asyncfunction(assert){
        assert.expect(11);

        constactionManager=awaitcreateActionManager({
            data:this.data,
            actions:[{
                id:11,
                name:'Action11',
                res_model:'foo',
                type:'ir.actions.act_window',
                views:[[3,'list']],
                search_view_id:[9,'search'],
                flags:{
                    context:{group_by:['int_field']},
                },
            }],
            archs:{
               'foo,3,list':'<treegroups_limit="3"><fieldname="foo"/></tree>',
               'foo,9,search':`
                    <search>
                        <filterstring="NotBar"name="notbar"domain="[['bar','=',False]]"/>
                    </search>`,
            },
            mockRPC:function(route,args){
                if(args.method==='web_read_group'){
                    assert.step(JSON.stringify(args.kwargs.domain)+','+args.kwargs.offset);
                }
                returnthis._super.apply(this,arguments);
            },
        });

        awaitactionManager.doAction(11);

        assert.containsOnce(actionManager,'.o_list_view');
        assert.strictEqual(actionManager.$('.o_pager_counter').text().trim(),'1-3/4');
        assert.containsN(actionManager,'.o_group_header',3);//page1

        awaittestUtils.dom.click(actionManager.$('.o_pager_next'));//switchtopage2

        assert.strictEqual(actionManager.$('.o_pager_counter').text().trim(),'4-4/4');
        assert.containsN(actionManager,'.o_group_header',1);//page2

        //toggleafilter->thereshouldbeonlyonegroupleft(onpage1)
        awaitcpHelpers.toggleFilterMenu(actionManager);
        awaitcpHelpers.toggleMenuItem(actionManager,0);

        assert.strictEqual(actionManager.$('.o_pager_counter').text().trim(),'1-1/1');
        assert.containsN(actionManager,'.o_group_header',1);//page1

        assert.verifySteps([
            '[],undefined',
            '[],3',
            '[["bar","=",false]],undefined',
        ]);

        actionManager.destroy();
    });

    QUnit.test('editablegroupedlists',asyncfunction(assert){
        assert.expect(4);

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<treeeditable="top"><fieldname="foo"/><fieldname="bar"/></tree>',
            groupBy:['bar'],
        });

        awaittestUtils.dom.click(list.$('.o_group_header:first'));//openfirstgroup

        //enteredition(groupedcase)
        awaittestUtils.dom.click(list.$('.o_data_cell:first'));
        assert.containsOnce(list,'.o_selected_row.o_data_cell:first');

        //clickonthebodyshouldleavetheedition
        awaittestUtils.dom.click($('body'));
        assert.containsNone(list,'.o_selected_row');

        //reloadwithoutgroupBy
        awaitlist.reload({groupBy:[]});

        //enteredition(ungroupedcase)
        awaittestUtils.dom.click(list.$('.o_data_cell:first'));
        assert.containsOnce(list,'.o_selected_row.o_data_cell:first');

        //clickonthebodyshouldleavetheedition
        awaittestUtils.dom.click($('body'));
        assert.containsNone(list,'.o_selected_row');

        list.destroy();
    });

    QUnit.test('groupedlistsareeditable(ungroupedfirst)',asyncfunction(assert){
        assert.expect(2);

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<treeeditable="top"><fieldname="foo"/><fieldname="bar"/></tree>',
        });

        //enteredition(ungroupedcase)
        awaittestUtils.dom.click(list.$('.o_data_cell:first'));
        assert.containsOnce(list,'.o_selected_row.o_data_cell:first');

        //reloadwithgroupBy
        awaitlist.reload({groupBy:['bar']});

        //openfirstgroup
        awaittestUtils.dom.click(list.$('.o_group_header:first'));

        //enteredition(groupedcase)
        awaittestUtils.dom.click(list.$('.o_data_cell:first'));
        assert.containsOnce(list,'.o_selected_row.o_data_cell:first');

        list.destroy();
    });

    QUnit.test('charfieldeditionineditablegroupedlist',asyncfunction(assert){
        assert.expect(2);

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<treeeditable="bottom"><fieldname="foo"/><fieldname="bar"/></tree>',
            groupBy:['bar'],
        });

        awaittestUtils.dom.click(list.$('.o_group_header:first'));//openfirstgroup
        awaittestUtils.dom.click(list.$('.o_data_cell:first'));
        awaittestUtils.fields.editAndTrigger(list.$('tr.o_selected_row.o_data_cell:firstinput[name="foo"]'),'pla','input');
        awaittestUtils.dom.click(list.$buttons.find('.o_list_button_save'));

        assert.strictEqual(this.data.foo.records[0].foo,'pla',
            "theeditionshouldhavebeenproperlysaved");
        assert.containsOnce(list,'.o_data_row:first:contains(pla)');

        list.destroy();
    });

    QUnit.test('controlpanelbuttonsineditablegroupedlistviews',asyncfunction(assert){
        assert.expect(2);

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<treeeditable="top"><fieldname="foo"/><fieldname="bar"/></tree>',
            groupBy:['bar'],
        });

        assert.isNotVisible(list.$buttons.find('.o_list_button_add'));

        //reloadwithoutgroupBy
        awaitlist.reload({groupBy:[]});
        assert.isVisible(list.$buttons.find('.o_list_button_add'));

        list.destroy();
    });

    QUnit.test('controlpanelbuttonsinmultieditablegroupedlistviews',asyncfunction(assert){
        assert.expect(8);

        constlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            groupBy:['foo'],
            arch:
                `<treemulti_edit="1">
                    <fieldname="foo"/>
                    <fieldname="int_field"/>
                </tree>`,
        });

        assert.containsNone(list,'.o_data_row',"allgroupsshouldbeclosed");
        assert.isVisible(list.$buttons.find('.o_list_button_add'),
            "shouldhaveavisibleCreatebutton");

        awaittestUtils.dom.click(list.$('.o_group_header:first'));
        assert.containsN(list,'.o_data_row',1,"firstgroupshouldbeopened");
        assert.isVisible(list.$buttons.find('.o_list_button_add'),
            "shouldhaveavisibleCreatebutton");

        awaittestUtils.dom.click(list.$('.o_data_row:eq(0).o_list_record_selectorinput'));
        assert.containsOnce(list,'.o_data_row:eq(0).o_list_record_selectorinput:enabled',
            "shouldhaveselectedfirstrecord");
        assert.isVisible(list.$buttons.find('.o_list_button_add'),
            "shouldhaveavisibleCreatebutton");

        awaittestUtils.dom.click(list.$('.o_group_header:last'));
        assert.containsN(list,'.o_data_row',2,"twogroupsshouldbeopened");
        assert.isVisible(list.$buttons.find('.o_list_button_add'),
            "shouldhaveavisibleCreatebutton");

        list.destroy();
    });

    QUnit.test('editalineanddiscarditingroupededitable',asyncfunction(assert){
        assert.expect(5);

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<treeeditable="top"><fieldname="foo"/><fieldname="int_field"/></tree>',
            groupBy:['bar'],
        });

        awaittestUtils.dom.click(list.$('.o_group_header:first'));
        awaittestUtils.dom.click(list.$('.o_data_row:nth(2)>td:contains(gnap)'));
        assert.ok(list.$('.o_data_row:nth(2)').is('.o_selected_row'),
            "thirdgrouprowshouldbeinedition");

        awaittestUtils.dom.click(list.$buttons.find('.o_list_button_discard'));
        awaittestUtils.dom.click(list.$('.o_data_row:nth(0)>td:contains(yop)'));
        assert.ok(list.$('.o_data_row:eq(0)').is('.o_selected_row'),
            "firstgrouprowshouldbeinedition");

        awaittestUtils.dom.click(list.$buttons.find('.o_list_button_discard'));
        assert.containsNone(list,'.o_selected_row');

        awaittestUtils.dom.click(list.$('.o_data_row:nth(2)>td:contains(gnap)'));
        assert.containsOnce(list,'.o_selected_row');
        assert.ok(list.$('.o_data_row:nth(2)').is('.o_selected_row'),
            "thirdgrouprowshouldbeinedition");

        list.destroy();
    });

    QUnit.test('addanddiscardarecordinamulti-levelgroupedlistview',asyncfunction(assert){
        assert.expect(7);

        testUtils.mock.patch(basicFields.FieldChar,{
            destroy:function(){
                assert.step('destroy');
                this._super.apply(this,arguments);
            },
        });

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<treeeditable="top"><fieldname="foo"required="1"/></tree>',
            groupBy:['foo','bar'],
        });

        //unfoldfirstsubgroup
        awaittestUtils.dom.click(list.$('.o_group_header:first'));
        awaittestUtils.dom.click(list.$('.o_group_header:eq(1)'));
        assert.hasClass(list.$('.o_group_header:first'),'o_group_open');
        assert.hasClass(list.$('.o_group_header:eq(1)'),'o_group_open');
        assert.containsOnce(list,'.o_data_row');

        //addarecordtofirstsubgroup
        awaittestUtils.dom.click(list.$('.o_group_field_row_adda'));
        assert.containsN(list,'.o_data_row',2);

        //discard
        awaittestUtils.dom.click(list.$buttons.find('.o_list_button_discard'));
        assert.containsOnce(list,'.o_data_row');

        assert.verifySteps(['destroy']);

        testUtils.mock.unpatch(basicFields.FieldChar);
        list.destroy();
    });

    QUnit.test('inputsaredisabledwhenunselectingrowsingroupededitable',asyncfunction(assert){
        assert.expect(1);

        var$input;
        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<treeeditable="bottom"><fieldname="foo"/></tree>',
            mockRPC:function(route,args){
                if(args.method==='write'){
                    assert.strictEqual($input.prop('disabled'),true,
                        "inputshouldbedisabled");
                }
                returnthis._super.apply(this,arguments);
            },
            groupBy:['bar'],
        });

        awaittestUtils.dom.click(list.$('.o_group_header:first'));
        awaittestUtils.dom.click(list.$('td:contains(yop)'));
        $input=list.$('tr.o_selected_rowinput[name="foo"]');
        awaittestUtils.fields.editAndTrigger($input,'lemon','input');
        awaittestUtils.fields.triggerKeydown($input,'tab');

        list.destroy();
    });

    QUnit.test('pressingESCineditablegroupedlistshoulddiscardthecurrentlinechanges',asyncfunction(assert){
        assert.expect(5);

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<treeeditable="top"><fieldname="foo"/><fieldname="bar"/></tree>',
            groupBy:['bar'],
        });

        awaittestUtils.dom.click(list.$('.o_group_header:first'));//openfirstgroup
        assert.containsN(list,'tr.o_data_row',3);

        awaittestUtils.dom.click(list.$('.o_data_cell:first'));

        //updatenameby"foo"
        awaittestUtils.fields.editAndTrigger(list.$('tr.o_selected_row.o_data_cell:firstinput[name="foo"]'),'new_value','input');
        //discardbypressingESC
        awaittestUtils.fields.triggerKeydown(list.$('input[name="foo"]'),'escape');
        awaittestUtils.dom.click($('.modal.modal-footer.btn-primary'));

        assert.containsOnce(list,'tbodytrtd:contains(yop)');
        assert.containsN(list,'tr.o_data_row',3);
        assert.containsNone(list,'tr.o_data_row.o_selected_row');
        assert.isNotVisible(list.$buttons.find('.o_list_button_save'));

        list.destroy();
    });

    QUnit.test('pressingTABineditable="bottom"groupedlist',asyncfunction(assert){
        assert.expect(7);

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<treeeditable="bottom"><fieldname="foo"/></tree>',
            groupBy:['bar'],
        });

        //opentwogroups
        awaittestUtils.dom.click(list.$('.o_group_header:first'));
        assert.containsN(list,'.o_data_row',3,'firstgroupcontains3rows');
        awaittestUtils.dom.click(list.$('.o_group_header:nth(1)'));
        assert.containsN(list,'.o_data_row',4,'firstgroupcontains1row');

        awaittestUtils.dom.click(list.$('.o_data_cell:first'));
        assert.hasClass(list.$('.o_data_row:first'),'o_selected_row');

        //Press'Tab'->shouldgotonextline(stillinfirstgroup)
        awaittestUtils.fields.triggerKeydown(list.$('.o_selected_row.o_input'),'tab');
        assert.hasClass(list.$('.o_data_row:nth(1)'),'o_selected_row');

        //Press'Tab'->shouldgotonextline(stillinfirstgroup)
        awaittestUtils.fields.triggerKeydown(list.$('.o_selected_row.o_input'),'tab');
        assert.hasClass(list.$('.o_data_row:nth(2)'),'o_selected_row');

        //Press'Tab'->shouldgotofirstlineofnextgroup
        awaittestUtils.fields.triggerKeydown(list.$('.o_selected_row.o_input'),'tab');
        assert.hasClass(list.$('.o_data_row:nth(3)'),'o_selected_row');

        //Press'Tab'->shouldgobacktofirstlineoffirstgroup
        awaittestUtils.fields.triggerKeydown(list.$('.o_selected_row.o_input'),'tab');
        assert.hasClass(list.$('.o_data_row:first'),'o_selected_row');

        list.destroy();
    });

    QUnit.test('pressingTABineditable="top"groupedlist',asyncfunction(assert){
        assert.expect(7);

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<treeeditable="top"><fieldname="foo"/></tree>',
            groupBy:['bar'],
        });

        //opentwogroups
        awaittestUtils.dom.click(list.$('.o_group_header:first'));
        assert.containsN(list,'.o_data_row',3,'firstgroupcontains3rows');
        awaittestUtils.dom.click(list.$('.o_group_header:nth(1)'));
        assert.containsN(list,'.o_data_row',4,'firstgroupcontains1row');

        awaittestUtils.dom.click(list.$('.o_data_cell:first'));

        assert.hasClass(list.$('.o_data_row:first'),'o_selected_row');

        //Press'Tab'->shouldgotonextline(stillinfirstgroup)
        awaittestUtils.fields.triggerKeydown(list.$('.o_selected_row.o_input'),'tab');
        assert.hasClass(list.$('.o_data_row:nth(1)'),'o_selected_row');

        //Press'Tab'->shouldgotonextline(stillinfirstgroup)
        awaittestUtils.fields.triggerKeydown(list.$('.o_selected_row.o_input'),'tab');
        assert.hasClass(list.$('.o_data_row:nth(2)'),'o_selected_row');

        //Press'Tab'->shouldgotofirstlineofnextgroup
        awaittestUtils.fields.triggerKeydown(list.$('.o_selected_row.o_input'),'tab');
        assert.hasClass(list.$('.o_data_row:nth(3)'),'o_selected_row');

        //Press'Tab'->shouldgobacktofirstlineoffirstgroup
        awaittestUtils.fields.triggerKeydown(list.$('.o_selected_row.o_input'),'tab');
        assert.hasClass(list.$('.o_data_row:first'),'o_selected_row');

        list.destroy();
    });

    QUnit.test('pressingTABineditablegroupedlistwithcreate=0',asyncfunction(assert){
        assert.expect(7);

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<treeeditable="bottom"create="0"><fieldname="foo"/></tree>',
            groupBy:['bar'],
        });

        //opentwogroups
        awaittestUtils.dom.click(list.$('.o_group_header:first'));
        assert.containsN(list,'.o_data_row',3,'firstgroupcontains3rows');
        awaittestUtils.dom.click(list.$('.o_group_header:nth(1)'));
        assert.containsN(list,'.o_data_row',4,'firstgroupcontains1row');

        awaittestUtils.dom.click(list.$('.o_data_cell:first'));

        assert.hasClass(list.$('.o_data_row:first'),'o_selected_row');

        //Press'Tab'->shouldgotonextline(stillinfirstgroup)
        awaittestUtils.fields.triggerKeydown(list.$('.o_selected_row.o_input'),'tab');
        assert.hasClass(list.$('.o_data_row:nth(1)'),'o_selected_row');

        //Press'Tab'->shouldgotonextline(stillinfirstgroup)
        awaittestUtils.fields.triggerKeydown(list.$('.o_selected_row.o_input'),'tab');
        assert.hasClass(list.$('.o_data_row:nth(2)'),'o_selected_row');

        //Press'Tab'->shouldgotofirstlineofnextgroup
        awaittestUtils.fields.triggerKeydown(list.$('.o_selected_row.o_input'),'tab');
        assert.hasClass(list.$('.o_data_row:nth(3)'),'o_selected_row');

        //Press'Tab'->shouldgobacktofirstlineoffirstgroup
        awaittestUtils.fields.triggerKeydown(list.$('.o_selected_row.o_input'),'tab');
        assert.hasClass(list.$('.o_data_row:first'),'o_selected_row');

        list.destroy();
    });

    QUnit.test('pressingSHIFT-TABineditable="bottom"groupedlist',asyncfunction(assert){
        assert.expect(6);

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<treeeditable="bottom"><fieldname="foo"required="1"/></tree>',
            groupBy:['bar'],
        });

        awaittestUtils.dom.click(list.$('.o_group_header:first'));//openfirstgroup
        assert.containsN(list,'.o_data_row',3,'firstgroupcontains3rows');
        awaittestUtils.dom.click(list.$('.o_group_header:eq(1)'));//opensecondgroup
        assert.containsN(list,'.o_data_row',4,'firstgroupcontains1row');

        //navigateinsideagroup
        awaittestUtils.dom.click(list.$('.o_data_row:eq(1).o_data_cell'));//selectsecondrowoffirstgroup
        assert.hasClass(list.$('tr.o_data_row:eq(1)'),'o_selected_row');

        //pressShft+tab
        list.$('tr.o_selected_rowinput').trigger($.Event('keydown',{which:$.ui.keyCode.TAB,shiftKey:true}));
        awaittestUtils.nextTick();
        assert.hasClass(list.$('tr.o_data_row:first'),'o_selected_row');
        assert.doesNotHaveClass(list.$('tr.o_data_row:eq(1)'),'o_selected_row');

        //navigatebetweengroups
        awaittestUtils.dom.click(list.$('.o_data_cell:eq(3)'));//selectrowofsecondgroup

        //pressShft+tab
        list.$('tr.o_selected_rowinput').trigger($.Event('keydown',{which:$.ui.keyCode.TAB,shiftKey:true}));
        awaittestUtils.nextTick();
        assert.hasClass(list.$('tr.o_data_row:eq(2)'),'o_selected_row');

        list.destroy();
    });

    QUnit.test('pressingSHIFT-TABineditable="top"groupedlist',asyncfunction(assert){
        assert.expect(6);

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<treeeditable="top"><fieldname="foo"required="1"/></tree>',
            groupBy:['bar'],
        });

        awaittestUtils.dom.click(list.$('.o_group_header:first'));//openfirstgroup
        assert.containsN(list,'.o_data_row',3,'firstgroupcontains3rows');
        awaittestUtils.dom.click(list.$('.o_group_header:eq(1)'));//opensecondgroup
        assert.containsN(list,'.o_data_row',4,'firstgroupcontains1row');

        //navigateinsideagroup
        awaittestUtils.dom.click(list.$('.o_data_row:eq(1).o_data_cell'));//selectsecondrowoffirstgroup
        assert.hasClass(list.$('tr.o_data_row:eq(1)'),'o_selected_row');

        //pressShft+tab
        list.$('tr.o_selected_rowinput').trigger($.Event('keydown',{which:$.ui.keyCode.TAB,shiftKey:true}));
        awaittestUtils.nextTick();
        assert.hasClass(list.$('tr.o_data_row:first'),'o_selected_row');
        assert.doesNotHaveClass(list.$('tr.o_data_row:eq(1)'),'o_selected_row');

        //navigatebetweengroups
        awaittestUtils.dom.click(list.$('.o_data_cell:eq(3)'));//selectrowofsecondgroup

        //pressShft+tab
        list.$('tr.o_selected_rowinput').trigger($.Event('keydown',{which:$.ui.keyCode.TAB,shiftKey:true}));
        awaittestUtils.nextTick();
        assert.hasClass(list.$('tr.o_data_row:eq(2)'),'o_selected_row');

        list.destroy();
    });

    QUnit.test('pressingSHIFT-TABineditablegroupedlistwithcreate="0"',asyncfunction(assert){
        assert.expect(6);

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<treeeditable="top"create="0"><fieldname="foo"required="1"/></tree>',
            groupBy:['bar'],
        });

        awaittestUtils.dom.click(list.$('.o_group_header:first'));//openfirstgroup
        assert.containsN(list,'.o_data_row',3,'firstgroupcontains3rows');
        awaittestUtils.dom.click(list.$('.o_group_header:eq(1)'));//opensecondgroup
        assert.containsN(list,'.o_data_row',4,'firstgroupcontains1row');

        //navigateinsideagroup
        awaittestUtils.dom.click(list.$('.o_data_row:eq(1).o_data_cell'));//selectsecondrowoffirstgroup
        assert.hasClass(list.$('tr.o_data_row:eq(1)'),'o_selected_row');

        //pressShft+tab
        list.$('tr.o_selected_rowinput').trigger($.Event('keydown',{which:$.ui.keyCode.TAB,shiftKey:true}));
        awaittestUtils.nextTick();
        assert.hasClass(list.$('tr.o_data_row:first'),'o_selected_row');
        assert.doesNotHaveClass(list.$('tr.o_data_row:eq(1)'),'o_selected_row');

        //navigatebetweengroups
        awaittestUtils.dom.click(list.$('.o_data_cell:eq(3)'));//selectrowofsecondgroup

        //pressShft+tab
        list.$('tr.o_selected_rowinput').trigger($.Event('keydown',{which:$.ui.keyCode.TAB,shiftKey:true}));
        awaittestUtils.nextTick();
        assert.hasClass(list.$('tr.o_data_row:eq(2)'),'o_selected_row');

        list.destroy();
    });

    QUnit.test('editingthenpressingTABineditablegroupedlist',asyncfunction(assert){
        assert.expect(19);

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<treeeditable="bottom"><fieldname="foo"/></tree>',
            mockRPC:function(route,args){
                assert.step(args.method||route);
                returnthis._super.apply(this,arguments);
            },
            groupBy:['bar'],
        });

        //opentwogroups
        awaittestUtils.dom.click(list.$('.o_group_header:first'));
        assert.containsN(list,'.o_data_row',3,'firstgroupcontains3rows');
        awaittestUtils.dom.click(list.$('.o_group_header:nth(1)'));
        assert.containsN(list,'.o_data_row',4,'firstgroupcontains1row');

        //selectandeditlastrowoffirstgroup
        awaittestUtils.dom.click(list.$('.o_data_row:nth(2).o_data_cell'));
        assert.hasClass(list.$('.o_data_row:nth(2)'),'o_selected_row');
        awaittestUtils.fields.editInput(list.$('.o_selected_rowinput[name="foo"]'),'newvalue');

        //Press'Tab'->shouldcreateanewrecordasweeditedthepreviousone
        awaittestUtils.fields.triggerKeydown(list.$('.o_selected_row.o_input'),'tab');
        assert.containsN(list,'.o_data_row',5);
        assert.hasClass(list.$('.o_data_row:nth(3)'),'o_selected_row');

        //fillfoofieldforthenewrecordandpress'tab'->shouldcreateanotherrecord
        awaittestUtils.fields.editInput(list.$('.o_selected_rowinput[name="foo"]'),'newrecord');
        awaittestUtils.fields.triggerKeydown(list.$('.o_selected_row.o_input'),'tab');

        assert.containsN(list,'.o_data_row',6);
        assert.hasClass(list.$('.o_data_row:nth(4)'),'o_selected_row');

        //leavethisnewrowemptyandpresstab->shoulddiscardthenewrecordandmovetothe
        //nextgroup
        awaittestUtils.fields.triggerKeydown(list.$('.o_selected_row.o_input'),'tab');
        assert.containsN(list,'.o_data_row',5);
        assert.hasClass(list.$('.o_data_row:nth(4)'),'o_selected_row');

        assert.verifySteps([
            'web_read_group',
            '/web/dataset/search_read',
            '/web/dataset/search_read',
            'write',
            'read',
            'onchange',
            'create',
            'read',
            'onchange',
        ]);

        list.destroy();
    });

    QUnit.test('editingthenpressingTAB(withareadonlyfield)ingroupedlist',asyncfunction(assert){
        assert.expect(6);

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<treeeditable="bottom"><fieldname="foo"/><fieldname="int_field"readonly="1"/></tree>',
            mockRPC:function(route,args){
                assert.step(args.method||route);
                returnthis._super.apply(this,arguments);
            },
            groupBy:['bar'],
            fieldDebounce:1
        });

        awaittestUtils.dom.click(list.$('.o_group_header:first'));//openfirstgroup
        //clickonfirsttdandpressTAB
        awaittestUtils.dom.click(list.$('td:contains(yop)'));
        awaittestUtils.fields.editAndTrigger(list.$('tr.o_selected_rowinput[name="foo"]'),'newvalue','input');
        awaittestUtils.fields.triggerKeydown(list.$('tr.o_selected_rowinput[name="foo"]'),'tab');

        assert.containsOnce(list,'tbodytrtd:contains(newvalue)');
        assert.verifySteps([
            'web_read_group',
            '/web/dataset/search_read',
            'write',
            'read',
        ]);

        list.destroy();
    });

    QUnit.test('pressingENTERineditable="bottom"groupedlistview',asyncfunction(assert){
        assert.expect(11);

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<treeeditable="bottom"><fieldname="foo"/></tree>',
            mockRPC:function(route,args){
                assert.step(args.method||route);
                returnthis._super.apply(this,arguments);
            },
            groupBy:['bar'],
        });

        awaittestUtils.dom.click(list.$('.o_group_header:first'));//openfirstgroup
        awaittestUtils.dom.click(list.$('.o_group_header:nth(1)'));//opensecondgroup
        assert.containsN(list,'tr.o_data_row',4);
        awaittestUtils.dom.click(list.$('.o_data_row:nth(1).o_data_cell'));//clickonsecondline
        assert.hasClass(list.$('tr.o_data_row:eq(1)'),'o_selected_row');

        //pressenterininputshouldmovetonextrecord
        awaittestUtils.fields.triggerKeydown(list.$('tr.o_selected_row.o_input'),'enter');

        assert.hasClass(list.$('tr.o_data_row:eq(2)'),'o_selected_row');
        assert.doesNotHaveClass(list.$('tr.o_data_row:eq(1)'),'o_selected_row');

        //pressenteronlastrowshouldcreateanewrecord
        awaittestUtils.fields.triggerKeydown(list.$('tr.o_selected_row.o_input'),'enter');

        assert.containsN(list,'tr.o_data_row',5);
        assert.hasClass(list.$('tr.o_data_row:eq(3)'),'o_selected_row');

        assert.verifySteps([
            'web_read_group',
            '/web/dataset/search_read',
            '/web/dataset/search_read',
            'onchange',
        ]);

        list.destroy();
    });

    QUnit.test('pressingENTERineditable="top"groupedlistview',asyncfunction(assert){
        assert.expect(10);

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<treeeditable="top"><fieldname="foo"/></tree>',
            mockRPC:function(route,args){
                assert.step(args.method||route);
                returnthis._super.apply(this,arguments);
            },
            groupBy:['bar'],
        });

        awaittestUtils.dom.click(list.$('.o_group_header:first'));//openfirstgroup
        awaittestUtils.dom.click(list.$('.o_group_header:nth(1)'));//opensecondgroup
        assert.containsN(list,'tr.o_data_row',4);
        awaittestUtils.dom.click(list.$('.o_data_row:nth(1).o_data_cell'));//clickonsecondline
        assert.hasClass(list.$('tr.o_data_row:eq(1)'),'o_selected_row');

        //pressenterininputshouldmovetonextrecord
        awaittestUtils.fields.triggerKeydown(list.$('tr.o_selected_row.o_input'),'enter');

        assert.hasClass(list.$('tr.o_data_row:eq(2)'),'o_selected_row');
        assert.doesNotHaveClass(list.$('tr.o_data_row:eq(1)'),'o_selected_row');

        //pressenteronlastrowshouldmovetofirstrecordofnextgroup
        awaittestUtils.fields.triggerKeydown(list.$('tr.o_selected_row.o_input'),'enter');

        assert.hasClass(list.$('tr.o_data_row:eq(3)'),'o_selected_row');
        assert.doesNotHaveClass(list.$('tr.o_data_row:eq(2)'),'o_selected_row');

        assert.verifySteps([
            'web_read_group',
            '/web/dataset/search_read',
            '/web/dataset/search_read',
        ]);

        list.destroy();
    });

    QUnit.test('pressingENTERineditablegroupedlistviewwithcreate=0',asyncfunction(assert){
        assert.expect(10);

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<treeeditable="bottom"create="0"><fieldname="foo"/></tree>',
            mockRPC:function(route,args){
                assert.step(args.method||route);
                returnthis._super.apply(this,arguments);
            },
            groupBy:['bar'],
        });

        awaittestUtils.dom.click(list.$('.o_group_header:first'));//openfirstgroup
        awaittestUtils.dom.click(list.$('.o_group_header:nth(1)'));//opensecondgroup
        assert.containsN(list,'tr.o_data_row',4);
        awaittestUtils.dom.click(list.$('.o_data_row:nth(1).o_data_cell'));//clickonsecondline
        assert.hasClass(list.$('tr.o_data_row:eq(1)'),'o_selected_row');

        //pressenterininputshouldmovetonextrecord
        awaittestUtils.fields.triggerKeydown(list.$('tr.o_selected_row.o_input'),'enter');

        assert.hasClass(list.$('tr.o_data_row:eq(2)'),'o_selected_row');
        assert.doesNotHaveClass(list.$('tr.o_data_row:eq(1)'),'o_selected_row');

        //pressenteronlastrowshouldmovetofirstrecordofnextgroup
        awaittestUtils.fields.triggerKeydown(list.$('tr.o_selected_row.o_input'),'enter');

        assert.hasClass(list.$('tr.o_data_row:eq(3)'),'o_selected_row');
        assert.doesNotHaveClass(list.$('tr.o_data_row:eq(2)'),'o_selected_row');

        assert.verifySteps([
            'web_read_group',
            '/web/dataset/search_read',
            '/web/dataset/search_read',
        ]);

        list.destroy();
    });

    QUnit.test('cell-levelkeyboardnavigationinnon-editablelist',asyncfunction(assert){
        assert.expect(16);

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<tree><fieldname="foo"required="1"/></tree>',
            intercepts:{
                switch_view:function(event){
                    assert.strictEqual(event.data.res_id,3,
                        "'switch_view'eventhasbeentriggered");
                },
            },
        });

        assert.ok(document.activeElement.classList.contains('o_searchview_input'),
            'defaultfocusshouldbeinsearchview');
        awaittestUtils.fields.triggerKeydown($(document.activeElement),'down');
        assert.strictEqual(document.activeElement.tagName,'INPUT',
            'focusshouldnowbeontherecordselector');
        awaittestUtils.fields.triggerKeydown($(document.activeElement),'up');
        assert.ok(document.activeElement.classList.contains('o_searchview_input'),
            'focusshouldhavecomebacktothesearchview');
        awaittestUtils.fields.triggerKeydown($(document.activeElement),'down');
        awaittestUtils.fields.triggerKeydown($(document.activeElement),'down');
        assert.strictEqual(document.activeElement.tagName,'INPUT',
            'focusshouldnowbeinfirstrowinput');
        awaittestUtils.fields.triggerKeydown($(document.activeElement),'right');
        assert.strictEqual(document.activeElement.tagName,'TD',
            'focusshouldnowbeinfieldTD');
        assert.strictEqual(document.activeElement.textContent,'yop',
            'focusshouldnowbeinfirstrowfield');
        awaittestUtils.fields.triggerKeydown($(document.activeElement),'right');
        assert.strictEqual(document.activeElement.textContent,'yop',
            'shouldnotcycleatendofline');
        awaittestUtils.fields.triggerKeydown($(document.activeElement),'down');
        assert.strictEqual(document.activeElement.textContent,'blip',
            'focusshouldnowbeinsecondrowfield');
        awaittestUtils.fields.triggerKeydown($(document.activeElement),'down');
        assert.strictEqual(document.activeElement.textContent,'gnap',
            'focusshouldnowbeinthirdrowfield');
        awaittestUtils.fields.triggerKeydown($(document.activeElement),'down');
        assert.strictEqual(document.activeElement.textContent,'blip',
            'focusshouldnowbeinlastrowfield');
        awaittestUtils.fields.triggerKeydown($(document.activeElement),'down');
        assert.strictEqual(document.activeElement.textContent,'blip',
            'focusshouldstillbeinlastrowfield(arrowsdonotcycle)');
        awaittestUtils.fields.triggerKeydown($(document.activeElement),'right');
        assert.strictEqual(document.activeElement.textContent,'blip',
            'focusshouldstillbeinlastrowfield(arrowsstilldonotcycle)');
        awaittestUtils.fields.triggerKeydown($(document.activeElement),'left');
        assert.strictEqual(document.activeElement.tagName,'INPUT',
            'focusshouldnowbeinlastrowinput');
        awaittestUtils.fields.triggerKeydown($(document.activeElement),'left');
        assert.strictEqual(document.activeElement.tagName,'INPUT',
            'shouldnotcycleatstartofline');
        awaittestUtils.fields.triggerKeydown($(document.activeElement),'up');
        awaittestUtils.fields.triggerKeydown($(document.activeElement),'right');
        assert.strictEqual(document.activeElement.textContent,'gnap',
            'focusshouldnowbeinthirdrowfield');
        awaittestUtils.fields.triggerKeydown($(document.activeElement),'enter');
        list.destroy();
    });

    QUnit.test('removingagroupbywhileaddingalinefromlist',asyncfunction(assert){
        assert.expect(1);

        letcheckUnselectRow=false;
        testUtils.mock.patch(ListRenderer,{
            unselectRow(options={}){
                if(checkUnselectRow){
                    assert.step('unselectRow');
                }
                returnthis._super(...arguments);
            },
        });

        constlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:`
                <treemulti_edit="1"editable="bottom">
                    <fieldname="display_name"/>
                    <fieldname="foo"/>
                </tree>
            `,
            archs:{
                'foo,false,search':`
                    <search>
                        <fieldname="foo"/>
                        <groupexpand="1"string="GroupBy">
                            <filtername="groupby_foo"context="{'group_by':'foo'}"/>
                        </group>
                    </search>
                `,
            },
        });

        awaitcpHelpers.toggleGroupByMenu(list);
        awaitcpHelpers.toggleMenuItem(list,0);
        //expandgroup
        awaittestUtils.dom.click(list.el.querySelector('th.o_group_name'));
        awaittestUtils.dom.click(list.el.querySelector('td.o_group_field_row_adda'));
        checkUnselectRow=true;
        awaittestUtils.dom.click($('.o_searchview_facet.o_facet_remove'));
        assert.verifySteps([]);
        testUtils.mock.unpatch(ListRenderer);
        list.destroy();
    });

    QUnit.test('cell-levelkeyboardnavigationineditablegroupedlist',asyncfunction(assert){
        assert.expect(56);

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<treeeditable="bottom"><fieldname="foo"required="1"/></tree>',
            groupBy:['bar'],
        });

        awaittestUtils.dom.click(list.$('.o_group_header:first'));//openfirstgroup
        awaittestUtils.dom.click(list.$('td:contains(blip)'));//selectrowoffirstgroup
        assert.hasClass(list.$('tr.o_data_row:eq(1)'),'o_selected_row',
            'secondrowshouldbeopened');

        var$secondRowInput=list.$('tr.o_data_row:eq(1)td:eq(1)input');
        assert.strictEqual($secondRowInput.val(),'blip',
            'secondrecordshouldbeineditmode');

        awaittestUtils.fields.editAndTrigger($secondRowInput,'blipbloup','input');
        assert.strictEqual($secondRowInput.val(),'blipbloup',
            'secondrecordshouldbechangedbutnotsavedyet');

        awaittestUtils.fields.triggerKeydown($(document.activeElement),'escape');

        assert.hasClass($('body'),'modal-open',
            'recordhasbeenmodified,areyousuremodalshouldbeopened');
        awaittestUtils.dom.click($('body.modalbuttonspan:contains(Ok)'));

        assert.doesNotHaveClass(list.$('tr.o_data_row:eq(1)'),'o_selected_row',
            'secondrowshouldbeclosed');
        assert.strictEqual(document.activeElement.tagName,'TD',
            'focusisinfieldtd');
        assert.strictEqual(document.activeElement.textContent,'blip',
            'secondfieldofsecondrecordshouldbefocused');
        assert.strictEqual(list.$('tr.o_data_row:eq(1)td:eq(1)').text(),'blip',
            'changeshouldnothavebeensaved');

        awaittestUtils.fields.triggerKeydown($(document.activeElement),'left');
        assert.strictEqual(document.activeElement.tagName,'INPUT',
            'recordselectorshouldbefocused');

        awaittestUtils.fields.triggerKeydown($(document.activeElement),'up');
        awaittestUtils.fields.triggerKeydown($(document.activeElement),'right');
        assert.strictEqual(document.activeElement.tagName,'TD',
            'focusisinfirstrecordtd');
        awaittestUtils.fields.triggerKeydown($(document.activeElement),'enter');
        var$firstRowInput=list.$('tr.o_data_row:eq(0)td:eq(1)input');
        assert.hasClass(list.$('tr.o_data_row:eq(0)'),'o_selected_row',
            'firstrowshouldbeselected');
        assert.strictEqual($firstRowInput.val(),'yop',
            'firstrecordshouldbeineditmode');

        awaittestUtils.fields.editAndTrigger($firstRowInput,'Zipadeedoodah','input');
        assert.strictEqual($firstRowInput.val(),'Zipadeedoodah',
            'firstrecordshouldbechangedbutnotsavedyet');
        awaittestUtils.fields.triggerKeydown($(document.activeElement),'enter');
        assert.strictEqual(list.$('tr.o_data_row:eq(0)td:eq(1)').text(),'Zipadeedoodah',
            'firstrecordshouldbesaved');
        assert.doesNotHaveClass(list.$('tr.o_data_row:eq(0)'),'o_selected_row',
            'firstrowshouldbeclosed');
        assert.hasClass(list.$('tr.o_data_row:eq(1)'),'o_selected_row',
            'secondrowshouldbeopened');
        assert.strictEqual(list.$('tr.o_data_row:eq(1)td:eq(1)input').val(),'blip',
            'secondrecordshouldbeineditmode');

        assert.strictEqual(document.activeElement.value,'blip',
            'secondrecordinputshouldbefocused');
        awaittestUtils.fields.triggerKeydown($(document.activeElement),'up');
        awaittestUtils.fields.triggerKeydown($(document.activeElement),'right');
        assert.strictEqual(document.activeElement.value,'blip',
            'secondrecordinputshouldstillbefocused(arrowsmovementsaredisabledinedit)');
        awaittestUtils.fields.triggerKeydown($(document.activeElement),'down');
        awaittestUtils.fields.triggerKeydown($(document.activeElement),'left');
        assert.strictEqual(document.activeElement.value,'blip',
            'secondrecordinputshouldstillbefocused(arrowsmovementsarestilldisabledinedit)');

        awaittestUtils.fields.triggerKeydown($(document.activeElement),'escape');
        assert.doesNotHaveClass(list.$('tr.o_data_row:eq(1)'),'o_selected_row',
            'secondrowshouldbeclosed');
        assert.strictEqual(document.activeElement.tagName,'TD',
            'focusisinfieldtd');
        assert.strictEqual(document.activeElement.textContent,'blip',
            'secondfieldofsecondrecordshouldbefocused');

        awaittestUtils.fields.triggerKeydown($(document.activeElement),'down');
        awaittestUtils.fields.triggerKeydown($(document.activeElement),'down');

        assert.strictEqual(document.activeElement.tagName,'A',
            'shouldfocusthe"Addaline"button');
        awaittestUtils.fields.triggerKeydown($(document.activeElement),'down');

        assert.strictEqual(document.activeElement.textContent,'false(1)',
            'focusshouldbeonsecondgroupheader');
        assert.strictEqual(list.$('tr.o_data_row').length,3,
            'shouldhave3rowsdisplayed');
        awaittestUtils.fields.triggerKeydown($(document.activeElement),'enter');
        assert.strictEqual(list.$('tr.o_data_row').length,4,
            'shouldhave4rowsdisplayed');
        assert.strictEqual(document.activeElement.textContent,'false(1)',
            'focusshouldstillbeonsecondgroupheader');

        awaittestUtils.fields.triggerKeydown($(document.activeElement),'down');
        assert.strictEqual(document.activeElement.textContent,'blip',
            'secondfieldoflastrecordshouldbefocused');
        awaittestUtils.fields.triggerKeydown($(document.activeElement),'down');
        assert.strictEqual(document.activeElement.tagName,'A',
            'shouldfocusthe"Addaline"button');
        awaittestUtils.fields.triggerKeydown($(document.activeElement),'down');
        assert.strictEqual(document.activeElement.tagName,'A',
            'arrownavigationshouldnotcycle(focusstillonlastrow)');

        awaittestUtils.fields.triggerKeydown($(document.activeElement),'enter');
        awaittestUtils.fields.editAndTrigger($('tr.o_data_row:eq(4)td:eq(1)input'),
            'cheateurarretedecheater','input');
        awaittestUtils.fields.triggerKeydown($(document.activeElement),'enter');
        assert.strictEqual(list.$('tr.o_data_row').length,6,
            'shouldhave6rowsdisplayed(newrecord+neweditline)');

        awaittestUtils.fields.triggerKeydown($(document.activeElement),'escape');
        assert.strictEqual(document.activeElement.tagName,'A',
            'shouldfocusthe"Addaline"button');

        //comebacktothetop
        awaittestUtils.fields.triggerKeydown($(document.activeElement),'up');
        awaittestUtils.fields.triggerKeydown($(document.activeElement),'up');
        awaittestUtils.fields.triggerKeydown($(document.activeElement),'up');
        awaittestUtils.fields.triggerKeydown($(document.activeElement),'up');
        awaittestUtils.fields.triggerKeydown($(document.activeElement),'up');
        awaittestUtils.fields.triggerKeydown($(document.activeElement),'up');
        awaittestUtils.fields.triggerKeydown($(document.activeElement),'up');
        awaittestUtils.fields.triggerKeydown($(document.activeElement),'up');
        awaittestUtils.fields.triggerKeydown($(document.activeElement),'up');

        assert.strictEqual(document.activeElement.tagName,'TH',
            'focusisintableheader');
        awaittestUtils.fields.triggerKeydown($(document.activeElement),'left');
        assert.strictEqual(document.activeElement.tagName,'INPUT',
            'focusisinheaderinput');
        awaittestUtils.fields.triggerKeydown($(document.activeElement),'down');
        awaittestUtils.fields.triggerKeydown($(document.activeElement),'down');
        awaittestUtils.fields.triggerKeydown($(document.activeElement),'right');
        assert.strictEqual(document.activeElement.tagName,'TD',
            'focusisinfieldtd');
        assert.strictEqual(document.activeElement.textContent,'Zipadeedoodah',
            'secondfieldoffirstrecordshouldbefocused');

        awaittestUtils.fields.triggerKeydown($(document.activeElement),'up');
        assert.strictEqual(document.activeElement.textContent,'true(3)',
            'focusshouldbeonfirstgroupheader');
        awaittestUtils.fields.triggerKeydown($(document.activeElement),'enter');
        assert.strictEqual(list.$('tr.o_data_row').length,2,
            'shouldhave2rowsdisplayed(firstgroupshouldbeclosed)');
        assert.strictEqual(document.activeElement.textContent,'true(3)',
            'focusshouldstillbeonfirstgroupheader');

        assert.strictEqual(list.$('tr.o_data_row').length,2,
            'shouldhave2rowsdisplayed');
        awaittestUtils.fields.triggerKeydown($(document.activeElement),'right');
        assert.strictEqual(list.$('tr.o_data_row').length,5,
            'shouldhave5rowsdisplayed');
        assert.strictEqual(document.activeElement.textContent,'true(3)',
            'focusisstillinheader');
        awaittestUtils.fields.triggerKeydown($(document.activeElement),'right');
        assert.strictEqual(list.$('tr.o_data_row').length,5,
            'shouldhave5rowsdisplayed');
        assert.strictEqual(document.activeElement.textContent,'true(3)',
            'focusisstillinheader');

        awaittestUtils.fields.triggerKeydown($(document.activeElement),'left');
        assert.strictEqual(list.$('tr.o_data_row').length,2,
            'shouldhave2rowsdisplayed');
        assert.strictEqual(document.activeElement.textContent,'true(3)',
            'focusisstillinheader');
        awaittestUtils.fields.triggerKeydown($(document.activeElement),'left');
        assert.strictEqual(list.$('tr.o_data_row').length,2,
            'shouldhave2rowsdisplayed');
        assert.strictEqual(document.activeElement.textContent,'true(3)',
            'focusisstillinheader');

        awaittestUtils.fields.triggerKeydown($(document.activeElement),'down');
        assert.strictEqual(document.activeElement.textContent,'false(2)',
            'focusshouldnowbeonsecondgroupheader');
        awaittestUtils.fields.triggerKeydown($(document.activeElement),'down');
        assert.strictEqual(document.activeElement.tagName,'TD',
            'recordtdshouldbefocused');
        assert.strictEqual(document.activeElement.textContent,'blip',
            'secondfieldoffirstrecordofsecondgroupshouldbefocused');

        awaittestUtils.fields.triggerKeydown($(document.activeElement),'down');
        assert.strictEqual(document.activeElement.textContent,'cheateurarretedecheater',
            'secondfieldoflastrecordofsecondgroupshouldbefocused');
        awaittestUtils.fields.triggerKeydown($(document.activeElement),'down');
        assert.strictEqual(document.activeElement.tagName,'A',
            'shouldfocusthe"Addaline"button');
        awaittestUtils.fields.triggerKeydown($(document.activeElement),'up');
        assert.strictEqual(document.activeElement.textContent,'cheateurarretedecheater',
        'secondfieldoflastrecordofsecondgroupshouldbefocused(specialcase:thefirsttdofthe"Addaline"linewasskipped');
        awaittestUtils.fields.triggerKeydown($(document.activeElement),'up');
        assert.strictEqual(document.activeElement.textContent,'blip',
            'secondfieldoffirstrecordofsecondgroupshouldbefocused');

        list.destroy();
    });

    QUnit.test('executegroupheaderbuttonwithkeyboardnavigation',asyncfunction(assert){
        assert.expect(13);

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<tree>'+
                    '<fieldname="foo"/>'+
                    '<groupbyname="m2o">'+
                        '<buttontype="object"name="some_method"string="Dothis"/>'+
                    '</groupby>'+
                '</tree>',
            groupBy:['m2o'],
            intercepts:{
                execute_action:function(ev){
                    assert.strictEqual(ev.data.action_data.name,'some_method');
                },
            },
        });

        assert.containsNone(list,'.o_data_row',"allgroupsshouldbeclosed");

        //focuscreatebuttonasastartingpoint
        list.$('.o_list_button_add').focus();
        assert.ok(document.activeElement.classList.contains('o_list_button_add'));
        awaittestUtils.fields.triggerKeydown($(document.activeElement),'down');
        assert.strictEqual(document.activeElement.tagName,'INPUT',
            'focusshouldnowbeontherecordselector(listheader)');
        awaittestUtils.fields.triggerKeydown($(document.activeElement),'down');
        assert.strictEqual(document.activeElement.textContent,'Value1(3)',
            'focusshouldbeonfirstgroupheader');

        //unfoldfirstgroup
        awaittestUtils.fields.triggerKeydown($(document.activeElement),'enter');
        assert.containsN(list,'.o_data_row',3,"firstgroupshouldbeopen");

        //movetofirstrecordofopenedgroup
        awaittestUtils.fields.triggerKeydown($(document.activeElement),'down');
        assert.strictEqual(document.activeElement.tagName,'INPUT',
            'focusshouldbeinfirstrowcheckbox');

        //movebacktothegroupheader
        awaittestUtils.fields.triggerKeydown($(document.activeElement),'up');
        assert.ok(document.activeElement.classList.contains('o_group_name'),
            'focusshouldbebackonfirstgroupheader');

        //foldthegroup
        awaittestUtils.fields.triggerKeydown($(document.activeElement),'enter');
        assert.ok(document.activeElement.classList.contains('o_group_name'),
            'focusshouldstillbeonfirstgroupheader');
        assert.containsNone(list,'.o_data_row',"firstgroupshouldnowbefolded");

        //unfoldthegroup
        awaittestUtils.fields.triggerKeydown($(document.activeElement),'enter');
        assert.ok(document.activeElement.classList.contains('o_group_name'),
            'focusshouldstillbeonfirstgroupheader');
        assert.containsN(list,'.o_data_row',3,"firstgroupshouldbeopen");

        //simulateamovetothegroupheaderbuttonwithtab(wecan'ttriggeranativeevent
        //programmatically,seehttps://stackoverflow.com/a/32429197)
        list.$('.o_group_header.o_group_buttonsbutton:first').focus();
        assert.strictEqual(document.activeElement.tagName,'BUTTON',
            'focusshouldbeonthegroupheaderbutton');

        //clickonthebuttonbypressingenter
        awaittestUtils.fields.triggerKeydown($(document.activeElement),'enter');
        assert.containsN(list,'.o_data_row',3,"firstgroupshouldstillbeopen");

        list.destroy();
    });

    QUnit.test('addanewrowingroupededitable="top"list',asyncfunction(assert){
        assert.expect(7);

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<treeeditable="top"><fieldname="foo"required="1"/></tree>',
            groupBy:['bar'],
        });

        awaittestUtils.dom.click(list.$('.o_group_header:first'));//opengroup
        awaittestUtils.dom.click(list.$('.o_group_field_row_adda'));//addanewrow
        assert.strictEqual(list.$('.o_selected_row.o_input[name=foo]')[0],document.activeElement,
            'Thefirstinputofthelineshouldhavethefocus');
        assert.containsN(list,'tbody:nth(1).o_data_row',4);

        awaittestUtils.dom.click(list.$buttons.find('.o_list_button_discard'));//discardnewrow
        awaittestUtils.dom.click(list.$('.o_group_header:eq(1)'));//opensecondgroup
        assert.containsOnce(list,'tbody:nth(3).o_data_row');

        awaittestUtils.dom.click(list.$('.o_group_field_row_adda:eq(1)'));//createrowinsecondgroup
        assert.strictEqual(list.$('.o_group_name:eq(1)').text(),'false(2)',
            "groupshouldhavecorrectnameandcount");
        assert.containsN(list,'tbody:nth(3).o_data_row',2);
        assert.hasClass(list.$('.o_data_row:nth(3)'),'o_selected_row');

        awaittestUtils.fields.editAndTrigger(list.$('tr.o_selected_rowinput[name="foo"]'),'pla','input');
        awaittestUtils.dom.click(list.$buttons.find('.o_list_button_save'));
        assert.containsN(list,'tbody:nth(3).o_data_row',2);

        list.destroy();
    });

    QUnit.test('addanewrowingroupededitable="bottom"list',asyncfunction(assert){
        assert.expect(5);

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<treeeditable="bottom"><fieldname="foo"required="1"/></tree>',
            groupBy:['bar'],
        });

        awaittestUtils.dom.click(list.$('.o_group_header:first'));//opengroup
        awaittestUtils.dom.click(list.$('.o_group_field_row_adda'));//addanewrow
        assert.hasClass(list.$('.o_data_row:nth(3)'),'o_selected_row');
        assert.containsN(list,'tbody:nth(1).o_data_row',4);

        awaittestUtils.dom.click(list.$buttons.find('.o_list_button_discard'));//discardnewrow
        awaittestUtils.dom.click(list.$('.o_group_header:eq(1)'));//opensecondgroup
        assert.containsOnce(list,'tbody:nth(3).o_data_row');
        awaittestUtils.dom.click(list.$('.o_group_field_row_adda:eq(1)'));//createrowinsecondgroup
        assert.hasClass(list.$('.o_data_row:nth(4)'),'o_selected_row');

        awaittestUtils.fields.editAndTrigger(list.$('tr.o_selected_rowinput[name="foo"]'),'pla','input');
        awaittestUtils.dom.click(list.$buttons.find('.o_list_button_save'));
        assert.containsN(list,'tbody:nth(3).o_data_row',2);

        list.destroy();
    });

    QUnit.test('addanddiscardalinethroughkeyboardnavigationwithoutcrashing',asyncfunction(assert){
        assert.expect(2);

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<treeeditable="bottom"><fieldname="foo"required="1"/></tree>',
            groupBy:['bar'],
        });

        awaittestUtils.dom.click(list.$('.o_group_header:first'));//opengroup
        //TriggersENTERon"Addaline"wrappercell
        awaittestUtils.fields.triggerKeydown(list.$('.o_group_field_row_add'),'enter');
        assert.containsN(list,'tbody:nth(1).o_data_row',4,"newdatarowshouldbecreated");
        awaittestUtils.dom.click(list.$buttons.find('.o_list_button_discard'));
        //Atthispoint,acrashmanagershouldappearifnoproperlinktargetting
        assert.containsN(list,'tbody:nth(1).o_data_row',3,"newdatarowshouldbediscarded.");

        list.destroy();
    });

    QUnit.test('editablegroupedlistwithcreate="0"',asyncfunction(assert){
        assert.expect(1);

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<treeeditable="top"create="0"><fieldname="foo"required="1"/></tree>',
            groupBy:['bar'],
        });

        awaittestUtils.dom.click(list.$('.o_group_header:first'));//opengroup
        assert.containsNone(list,'.o_group_field_row_adda',
            "Addalineshouldnotbeavailableinreadonly");

        list.destroy();
    });

    QUnit.test('addanewrowin(selection)groupededitablelist',asyncfunction(assert){
        assert.expect(6);

        this.data.foo.fields.priority={
            string:"Priority",
            type:"selection",
            selection:[[1,"Low"],[2,"Medium"],[3,"High"]],
            default:1,
        };
        this.data.foo.records.push({id:5,foo:"blip",int_field:-7,m2o:1,priority:2});
        this.data.foo.records.push({id:6,foo:"blip",int_field:5,m2o:1,priority:3});

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<treeeditable="top">'+
                        '<fieldname="foo"/>'+
                        '<fieldname="priority"/>'+
                        '<fieldname="m2o"/>'+
                    '</tree>',
            groupBy:['priority'],
            mockRPC:function(route,args){
                if(args.method==='onchange'){
                    assert.step(args.kwargs.context.default_priority.toString());
                }
                returnthis._super.apply(this,arguments);
            },
        });

        awaittestUtils.dom.click(list.$('.o_group_header:first'));//opengroup
        awaittestUtils.dom.click(list.$('.o_group_field_row_adda'));//addanewrow
        awaittestUtils.dom.click($('body'));//unselectrow
        assert.verifySteps(['1']);
        assert.strictEqual(list.$('.o_data_row.o_data_cell:eq(1)').text(),'Low',
            "shouldhaveacolumnnamewithavaluefromthegroupby");

        awaittestUtils.dom.click(list.$('.o_group_header:eq(1)'));//opensecondgroup
        awaittestUtils.dom.click(list.$('.o_group_field_row_adda:eq(1)'));//createrowinsecondgroup
        awaittestUtils.dom.click($('body'));//unselectrow
        assert.strictEqual(list.$('.o_data_row:nth(5).o_data_cell:eq(1)').text(),'Medium',
            "shouldhaveacolumnnamewithavaluefromthegroupby");
        assert.verifySteps(['2']);

        list.destroy();
    });

    QUnit.test('addanewrowin(m2o)groupededitablelist',asyncfunction(assert){
        assert.expect(6);

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<treeeditable="top">'+
                        '<fieldname="foo"/>'+
                        '<fieldname="m2o"/>'+
                    '</tree>',
            groupBy:['m2o'],
            mockRPC:function(route,args){
                if(args.method==='onchange'){
                    assert.step(args.kwargs.context.default_m2o.toString());
                }
                returnthis._super.apply(this,arguments);
            },
        });

        awaittestUtils.dom.click(list.$('.o_group_header:first'));
        awaittestUtils.dom.click(list.$('.o_group_field_row_adda'));
        awaittestUtils.dom.click($('body'));//unselectrow
        assert.strictEqual(list.$('tbody:eq(1).o_data_row:first.o_data_cell:eq(1)').text(),'Value1',
            "shouldhaveacolumnnamewithavaluefromthegroupby");
        assert.verifySteps(['1']);

        awaittestUtils.dom.click(list.$('.o_group_header:eq(1)'));//opensecondgroup
        awaittestUtils.dom.click(list.$('.o_group_field_row_adda:eq(1)'));//createrowinsecondgroup
        awaittestUtils.dom.click($('body'));//unselectrow
        assert.strictEqual(list.$('tbody:eq(3).o_data_row:first.o_data_cell:eq(1)').text(),'Value2',
            "shouldhaveacolumnnamewithavaluefromthegroupby");
        assert.verifySteps(['2']);

        list.destroy();
    });

    QUnit.test('listviewwithoptionalfieldsrendering',asyncfunction(assert){
        assert.expect(12);

        varRamStorageService=AbstractStorageService.extend({
            storage:newRamStorage(),
        });

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<tree>'+
                    '<fieldname="foo"/>'+
                    '<fieldname="m2o"optional="hide"/>'+
                    '<fieldname="amount"/>'+
                    '<fieldname="reference"optional="hide"/>'+
                '</tree>',
            services:{
                local_storage:RamStorageService,
            },
            translateParameters:{
                direction:'ltr',
            }
        });

        assert.containsN(list,'th',3,
            "shouldhave3th,1forselector,2forcolumns");

        assert.containsOnce(list.$('table'),'.o_optional_columns_dropdown_toggle',
            "shouldhavetheoptionalcolumnsdropdowntoggleinsidethetable");

        constoptionalFieldsToggler=list.el.querySelector('table').lastElementChild;
        assert.ok(optionalFieldsToggler.classList.contains('o_optional_columns_dropdown_toggle'),
            'Theoptionalfieldstoggleristhesecondlastelement');
        constoptionalFieldsDropdown=list.el.querySelector('.o_list_view').lastElementChild;
        assert.ok(optionalFieldsDropdown.classList.contains('o_optional_columns'),
            'Theoptionalfieldsdropdownisthelastelement');

        assert.ok(list.$('.o_optional_columns.dropdown-menu').hasClass('dropdown-menu-right'),
            'InLTR,thedropdownshouldbeanchoredtotherightandexpandtotheleft');

        //optionalfields
        awaittestUtils.dom.click(list.$('table.o_optional_columns_dropdown_toggle'));
        assert.containsN(list,'div.o_optional_columnsdiv.dropdown-item',2,
            "dropdownhave2optionalfieldfoowithcheckedandbarwithunchecked");

        //enableoptionalfield
        awaittestUtils.dom.click(list.$('div.o_optional_columnsdiv.dropdown-item:firstinput'));
        //5th(1forcheckbox,4forcolumns)
        assert.containsN(list,'th',4,"shouldhave4th");
        assert.ok(list.$('th:contains(M2Ofield)').is(':visible'),
            "shouldhaveavisiblem2ofield");//m2ofield

        //disableoptionalfield
        awaittestUtils.dom.click(list.$('table.o_optional_columns_dropdown_toggle'));
        assert.strictEqual(list.$('div.o_optional_columnsdiv.dropdown-item:firstinput:checked')[0],
            list.$('div.o_optional_columnsdiv.dropdown-item[name="m2o"]')[0],
            "m2oadvancedfieldcheckboxshouldbecheckedindropdown");

        awaittestUtils.dom.click(list.$('div.o_optional_columnsdiv.dropdown-item:firstinput'));
        //3th(1forcheckbox,2forcolumns)
        assert.containsN(list,'th',3,"shouldhave3th");
        assert.notOk(list.$('th:contains(M2Ofield)').is(':visible'),
            "shouldnothaveavisiblem2ofield");//m2ofieldnotdisplayed

        awaittestUtils.dom.click(list.$('table.o_optional_columns_dropdown_toggle'));
        assert.notOk(list.$('div.o_optional_columnsdiv.dropdown-item[name="m2o"]').is(":checked"));

        list.destroy();
    });

    QUnit.test('listviewwithoptionalfieldsrenderinginRTLmode',asyncfunction(assert){
        assert.expect(4);

        varRamStorageService=AbstractStorageService.extend({
            storage:newRamStorage(),
        });

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<tree>'+
                    '<fieldname="foo"/>'+
                    '<fieldname="m2o"optional="hide"/>'+
                    '<fieldname="amount"/>'+
                    '<fieldname="reference"optional="hide"/>'+
                '</tree>',
            services:{
                local_storage:RamStorageService,
            },
            translateParameters:{
                direction:'rtl',
            }
        });

        assert.containsOnce(list.$('table'),'.o_optional_columns_dropdown_toggle',
            "shouldhavetheoptionalcolumnsdropdowntoggleinsidethetable");

        constoptionalFieldsToggler=list.el.querySelector('table').lastElementChild;
        assert.ok(optionalFieldsToggler.classList.contains('o_optional_columns_dropdown_toggle'),
            'Theoptionalfieldstoggleristhelastelement');
        constoptionalFieldsDropdown=list.el.querySelector('.o_list_view').lastElementChild;
        assert.ok(optionalFieldsDropdown.classList.contains('o_optional_columns'),
            'Theoptionalfieldsisthelastelement');

        assert.ok(list.$('.o_optional_columns.dropdown-menu').hasClass('dropdown-menu-left'),
            'InRTL,thedropdownshouldbeanchoredtotheleftandexpandtotheright');

        list.destroy();
    });

    QUnit.test('optionalfieldsdonotdisappearevenafterlistviewreload',asyncfunction(assert){
        assert.expect(7);

        varRamStorageService=AbstractStorageService.extend({
            storage:newRamStorage(),
        });

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<tree>'+
                    '<fieldname="foo"/>'+
                    '<fieldname="m2o"optional="hide"/>'+
                    '<fieldname="amount"/>'+
                    '<fieldname="reference"optional="hide"/>'+
                '</tree>',
            services:{
                local_storage:RamStorageService,
            },
        });

        assert.containsN(list,'th',3,
            "shouldhave3th,1forselector,2forcolumns");

        //enableoptionalfield
        awaittestUtils.dom.click(list.$('table.o_optional_columns_dropdown_toggle'));
        assert.notOk(list.$('div.o_optional_columnsdiv.dropdown-item[name="m2o"]').is(":checked"));
        awaittestUtils.dom.click(list.$('div.o_optional_columnsdiv.dropdown-item:firstinput'));
        assert.containsN(list,'th',4,
            "shouldhave4th1forselector,3forcolumns");
        assert.ok(list.$('th:contains(M2Ofield)').is(':visible'),
            "shouldhaveavisiblem2ofield");//m2ofield

        //reloadlistview
        awaitlist.reload();
        assert.containsN(list,'th',4,
            "shouldhave4th1forselector,3forcolumnseverafterlistviewreload");
        assert.ok(list.$('th:contains(M2Ofield)').is(':visible'),
            "shouldhaveavisiblem2ofieldevenafterlistviewreload");

        awaittestUtils.dom.click(list.$('table.o_optional_columns_dropdown_toggle'));
        assert.ok(list.$('div.o_optional_columnsdiv.dropdown-item[name="m2o"]').is(":checked"));

        list.destroy();
    });

    QUnit.test('selectioniskeptwhenoptionalfieldsaretoggled',asyncfunction(assert){
        assert.expect(7);

        varRamStorageService=AbstractStorageService.extend({
            storage:newRamStorage(),
        });

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<tree>'+
                    '<fieldname="foo"/>'+
                    '<fieldname="m2o"optional="hide"/>'+
                '</tree>',
            services:{
                local_storage:RamStorageService,
            },
        });

        assert.containsN(list,'th',2);

        //selectarecord
        awaittestUtils.dom.click(list.$('.o_data_row.o_list_record_selectorinput:first'));

        assert.containsOnce(list,'.o_list_record_selectorinput:checked');

        //addanoptionalfield
        awaittestUtils.dom.click(list.$('table.o_optional_columns_dropdown_toggle'));
        awaittestUtils.dom.click(list.$('div.o_optional_columnsdiv.dropdown-item:firstinput'));
        assert.containsN(list,'th',3);

        assert.containsOnce(list,'.o_list_record_selectorinput:checked');

        //selectallrecords
        awaittestUtils.dom.click(list.$('thead.o_list_record_selectorinput'));

        assert.containsN(list,'.o_list_record_selectorinput:checked',5);

        //removeanoptionalfield
        awaittestUtils.dom.click(list.$('table.o_optional_columns_dropdown_toggle'));
        awaittestUtils.dom.click(list.$('div.o_optional_columnsdiv.dropdown-item:firstinput'));
        assert.containsN(list,'th',2);

        assert.containsN(list,'.o_list_record_selectorinput:checked',5);

        list.destroy();
    });

    QUnit.test('listviewwithoptionalfieldsandasyncrendering',asyncfunction(assert){
        assert.expect(14);

        constprom=testUtils.makeTestPromise();
        constFieldChar=fieldRegistry.get('char');
        fieldRegistry.add('asyncwidget',FieldChar.extend({
            async_render(){
                assert.ok(true,'therenderingmustbeasync');
                this._super(...arguments);
                awaitprom;
            },
        }));

        constRamStorageService=AbstractStorageService.extend({
            storage:newRamStorage(),
        });

        constlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:`
                <tree>
                    <fieldname="m2o"/>
                    <fieldname="foo"widget="asyncwidget"optional="hide"/>
                </tree>`,
            services:{
                local_storage:RamStorageService,
            },
        });

        assert.containsN(list,'th',2);
        assert.isNotVisible(list.$('.o_optional_columns_dropdown'));

        //addanoptionalfield(weclickonthelabelonpurpose,asitwilltrigger
        //asecondeventontheinput)
        awaittestUtils.dom.click(list.$('table.o_optional_columns_dropdown_toggle'));
        assert.isVisible(list.$('.o_optional_columns_dropdown'));
        assert.containsNone(list.$('.o_optional_columns_dropdown'),'input:checked');
        awaittestUtils.dom.click(list.$('div.o_optional_columnsdiv.dropdown-item:firstlabel'));

        assert.containsN(list,'th',2);
        assert.isVisible(list.$('.o_optional_columns_dropdown'));
        assert.containsNone(list.$('.o_optional_columns_dropdown'),'input:checked');

        prom.resolve();
        awaittestUtils.nextTick();

        assert.containsN(list,'th',3);
        assert.isVisible(list.$('.o_optional_columns_dropdown'));
        assert.containsOnce(list.$('.o_optional_columns_dropdown'),'input:checked');

        list.destroy();
        deletefieldRegistry.map.asyncwidget;
    });

    QUnit.test('openlistoptionalfieldsdropdownpositiontorightplace',asyncfunction(assert){
        assert.expect(1);

        this.data.bar.fields.name={string:"Name",type:"char",sortable:true};
        this.data.bar.fields.foo={string:"Foo",type:"char",sortable:true};
        this.data.foo.records[0].o2m=[1,2];

        constform=awaitcreateView({
            View:FormView,
            model:'foo',
            data:this.data,
            arch:`
                <form>
                    <sheet>
                        <notebook>
                            <pagestring="Page1">
                                <fieldname="o2m">
                                    <treeeditable="bottom">
                                        <fieldname="display_name"/>
                                        <fieldname="foo"/>
                                        <fieldname="name"optional="hide"/>
                                    </tree>
                                </field>
                            </page>
                        </notebook>
                    </sheet>
                </form>`,
            res_id:1,
        });

        constlistWidth=form.el.querySelector('.o_list_view').offsetWidth;

        awaittestUtils.dom.click(form.el.querySelector('.o_optional_columns_dropdown_toggle'));
        assert.strictEqual(form.el.querySelector('.o_optional_columns').offsetLeft,listWidth,
            "optionalfieldsdropdownshouldopenedatrightplace");

        form.destroy();
    });

    QUnit.test('changetheviewTypeofthecurrentaction',asyncfunction(assert){
        assert.expect(25);

        this.actions=[{
            id:1,
            name:'PartnersAction1',
            res_model:'foo',
            type:'ir.actions.act_window',
            views:[[1,'kanban']],
        },{
            id:2,
            name:'Partners',
            res_model:'foo',
            type:'ir.actions.act_window',
            views:[[false,'list'],[1,'kanban']],
        }];

        this.archs={
            'foo,1,kanban':'<kanban><templates><tt-name="kanban-box">'+
            '<divclass="oe_kanban_global_click"><fieldname="foo"/></div>'+
            '</t></templates></kanban>',

            'foo,false,list':'<treelimit="3">'+
            '<fieldname="foo"/>'+
            '<fieldname="m2o"optional="hide"/>'+
            '<fieldname="o2m"optional="show"/></tree>',

            'foo,false,search':'<search><fieldname="foo"string="Foo"/></search>',
        };

        varRamStorageService=AbstractStorageService.extend({
            storage:newRamStorage(),
        });

        varactionManager=awaittestUtils.createActionManager({
            actions:this.actions,
            archs:this.archs,
            data:this.data,
            services:{
                local_storage:RamStorageService,
            },
        });
        awaitactionManager.doAction(2);

        assert.containsOnce(actionManager,'.o_list_view',
            "shouldhaverenderedalistview");

        assert.containsN(actionManager,'th',3,"shoulddisplay3th(selector+2fields)");

        //enableoptionalfield
        awaittestUtils.dom.click(actionManager.$('table.o_optional_columns_dropdown_toggle'));
        assert.notOk(actionManager.$('div.o_optional_columnsdiv.dropdown-item[name="m2o"]').is(":checked"));
        assert.ok(actionManager.$('div.o_optional_columnsdiv.dropdown-item[name="o2m"]').is(":checked"));
        awaittestUtils.dom.click(actionManager.$('div.o_optional_columnsdiv.dropdown-item:first'));
        assert.containsN(actionManager,'th',4,"shoulddisplay4th(selector+3fields)");
        assert.ok(actionManager.$('th:contains(M2Ofield)').is(':visible'),
            "shouldhaveavisiblem2ofield");//m2ofield

        //switchtokanbanview
        awaitactionManager.loadState({
            action:2,
            view_type:'kanban',
        });

        assert.containsNone(actionManager,'.o_list_view',
            "shouldnotdisplaythelistviewanymore");
        assert.containsOnce(actionManager,'.o_kanban_view',
            "shouldhaveswitchedtothekanbanview");

        //switchbacktolistview
        awaitactionManager.loadState({
            action:2,
            view_type:'list',
        });

        assert.containsNone(actionManager,'.o_kanban_view',
            "shouldnotdisplaythekanbanviewanymoe");
        assert.containsOnce(actionManager,'.o_list_view',
            "shoulddisplaythelistview");

        assert.containsN(actionManager,'th',4,"shoulddisplay4th");
        assert.ok(actionManager.$('th:contains(M2Ofield)').is(':visible'),
            "shouldhaveavisiblem2ofield");//m2ofield
        assert.ok(actionManager.$('th:contains(O2Mfield)').is(':visible'),
            "shouldhaveavisibleo2mfield");//m2ofield

        //disableoptionalfield
        awaittestUtils.dom.click(actionManager.$('table.o_optional_columns_dropdown_toggle'));
        assert.ok(actionManager.$('div.o_optional_columnsdiv.dropdown-item[name="m2o"]').is(":checked"));
        assert.ok(actionManager.$('div.o_optional_columnsdiv.dropdown-item[name="o2m"]').is(":checked"));
        awaittestUtils.dom.click(actionManager.$('div.o_optional_columnsdiv.dropdown-item:lastinput'));
        assert.ok(actionManager.$('th:contains(M2Ofield)').is(':visible'),
            "shouldhaveavisiblem2ofield");//m2ofield
        assert.notOk(actionManager.$('th:contains(O2Mfield)').is(':visible'),
            "shouldhaveavisibleo2mfield");//m2ofield
        assert.containsN(actionManager,'th',3,"shoulddisplay3th");

        awaitactionManager.doAction(1);

        assert.containsNone(actionManager,'.o_list_view',
            "shouldnotdisplaythelistviewanymore");
        assert.containsOnce(actionManager,'.o_kanban_view',
            "shouldhaveswitchedtothekanbanview");

        awaitactionManager.doAction(2);

        assert.containsNone(actionManager,'.o_kanban_view',
            "shouldnothavethekanbanviewanymoe");
        assert.containsOnce(actionManager,'.o_list_view',
            "shoulddisplaythelistview");

        assert.containsN(actionManager,'th',3,"shoulddisplay3th");
        assert.ok(actionManager.$('th:contains(M2Ofield)').is(':visible'),
            "shouldhaveavisiblem2ofield");//m2ofield
        assert.notOk(actionManager.$('th:contains(O2Mfield)').is(':visible'),
            "shouldhaveavisibleo2mfield");//m2ofield

        actionManager.destroy();
    });

    QUnit.test('listviewwithoptionalfieldsrenderingandlocalstoragemock',asyncfunction(assert){
        assert.expect(12);

        varforceLocalStorage=true;

        varStorage=RamStorage.extend({
            getItem:function(key){
                assert.step('getItem'+key);
                returnforceLocalStorage?'["m2o"]':this._super.apply(this,arguments);
            },
            setItem:function(key,value){
                assert.step('setItem'+key+'to'+value);
                returnthis._super.apply(this,arguments);
            },
        });

        varRamStorageService=AbstractStorageService.extend({
            storage:newStorage(),
        });

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<tree>'+
                '<fieldname="foo"/>'+
                '<fieldname="m2o"optional="hide"/>'+
                '<fieldname="reference"optional="show"/>'+
                '</tree>',
            services:{
                local_storage:RamStorageService,
            },
            view_id:42,
        });

        varlocalStorageKey='optional_fields,foo,list,42,foo,m2o,reference';

        assert.verifySteps(['getItem'+localStorageKey]);

        assert.containsN(list,'th',3,
            "shouldhave3th,1forselector,2forcolumns");

        assert.ok(list.$('th:contains(M2Ofield)').is(':visible'),
            "shouldhaveavisiblem2ofield");//m2ofield

        assert.notOk(list.$('th:contains(ReferenceField)').is(':visible'),
            "shouldnothaveavisiblereferencefield");

        //optionalfields
        awaittestUtils.dom.click(list.$('table.o_optional_columns_dropdown_toggle'));
        assert.containsN(list,'div.o_optional_columnsdiv.dropdown-item',2,
            "dropdownhave2optionalfields");

        forceLocalStorage=false;
        //enableoptionalfield
        awaittestUtils.dom.click(list.$('div.o_optional_columnsdiv.dropdown-item:eq(1)input'));

        assert.verifySteps([
            'setItem'+localStorageKey+'to["m2o","reference"]',
            'getItem'+localStorageKey,
        ]);

        //4th(1forcheckbox,3forcolumns)
        assert.containsN(list,'th',4,"shouldhave4th");

        assert.ok(list.$('th:contains(M2Ofield)').is(':visible'),
            "shouldhaveavisiblem2ofield");//m2ofield

        assert.ok(list.$('th:contains(ReferenceField)').is(':visible'),
            "shouldhaveavisiblereferencefield");

        list.destroy();
    });
    QUnit.test("quickcreateinamany2oneinalist",asyncfunction(assert){
        assert.expect(2);

        constlist=awaitcreateView({
            arch:'<treeeditable="top"><fieldname="m2o"/></tree>',
            data:this.data,
            model:'foo',
            View:ListView,
        });

        awaittestUtils.dom.click(list.$('.o_data_row:first.o_data_cell:first'));

        const$input=list.$('.o_data_row:first.o_data_cell:firstinput');
        awaittestUtils.fields.editInput($input,"aaa");
        $input.trigger('keyup');
        $input.trigger('blur');
        document.body.click();

        awaittestUtils.nextTick();

        assert.containsOnce(document.body,'.modal',"thequick_createmodalshouldappear");

        awaittestUtils.dom.click($('.modal.btn-primary:first'));
        awaittestUtils.dom.click(document.body);

        assert.strictEqual(list.el.getElementsByClassName('o_data_cell')[0].innerHTML,"aaa",
            "valueshouldhavebeenupdated");

        list.destroy();
    });

    QUnit.test('floatfieldrenderwithdigitsattributeonlistview',asyncfunction(assert){
        assert.expect(1);

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<tree><fieldname="foo"/><fieldname="qux"digits="[12,6]"/></tree>',
        });

        assert.strictEqual(list.$('td.o_list_number:eq(0)').text(),"0.400000","shouldcontain6digitsdecimalprecision");
        list.destroy();
    });
    //TODO:writeteston:
    //-default_getwithafieldnotinview

    QUnit.test('editablelist:resizecolumnheaders',asyncfunction(assert){
        assert.expect(2);

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<treeeditable="top">'+
                    '<fieldname="foo"/>'+
                    '<fieldname="reference"optional="hide"/>'+
                '</tree>',
        });

        //Targethandle
        constth=list.el.getElementsByTagName('th')[1];
        constoptionalDropdown=list.el.getElementsByClassName('o_optional_columns')[0];
        constoptionalInitialX=optionalDropdown.getBoundingClientRect().x;
        constresizeHandle=th.getElementsByClassName('o_resize')[0];
        constoriginalWidth=th.offsetWidth;
        constexpectedWidth=Math.floor(originalWidth/2+resizeHandle.offsetWidth/2);
        constdelta=originalWidth-expectedWidth;

        awaittestUtils.dom.dragAndDrop(resizeHandle,th,{mousemoveTarget:window,mouseupTarget:window});
        constoptionalFinalX=Math.floor(optionalDropdown.getBoundingClientRect().x);

        assert.strictEqual(th.offsetWidth,expectedWidth,
            //1pxforthecellrightborder
            "headerwidthshouldbehalved(plushalfthewidthofthehandle)");
        assert.strictEqual(optionalFinalX,optionalInitialX-delta,
            "optionalcolumnsdropdownshouldhavemovedthesameamount");

        list.destroy();
    });

    QUnit.test('editablelist:resizecolumnheaderswithmax-width',asyncfunction(assert){
        //Thistestwillensurethat,onresizelistheader,
        //theresizedelementhavethecorrectsizeandotherelementsarenotresized
        assert.expect(2);
        this.data.foo.records[0].foo="a".repeat(200);

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<treeeditable="top">'+
                    '<fieldname="foo"/>'+
                    '<fieldname="bar"/>'+
                    '<fieldname="reference"optional="hide"/>'+
                '</tree>',
        });

        //Targethandle
        constth=list.el.getElementsByTagName('th')[1];
        constthNext=list.el.getElementsByTagName('th')[2];
        constresizeHandle=th.getElementsByClassName('o_resize')[0];
        constnextResizeHandle=thNext.getElementsByClassName('o_resize')[0];
        constthOriginalWidth=th.offsetWidth;
        constthNextOriginalWidth=thNext.offsetWidth;
        constthExpectedWidth=Math.floor(thOriginalWidth+thNextOriginalWidth);

        awaittestUtils.dom.dragAndDrop(resizeHandle,nextResizeHandle,{mousemoveTarget:window,mouseupTarget:window});

        constthFinalWidth=th.offsetWidth;
        constthNextFinalWidth=thNext.offsetWidth;
        constthWidthDiff=Math.abs(thExpectedWidth-thFinalWidth)

        assert.ok(thWidthDiff<=1,"Wrongwidthonresize");
        assert.ok(thNextOriginalWidth===thNextFinalWidth,"Widthmustnothavebeenchanged");

        list.destroy();
    });

    QUnit.test('resizecolumnwithseveralx2manylistsinformgroup',asyncfunction(assert){
        assert.expect(3);

        this.data.bar.fields.text={string:"Textfield",type:"char"};
        this.data.foo.records[0].o2m=[1,2];

        constform=awaitcreateView({
            View:FormView,
            model:'foo',
            data:this.data,
            arch:`
                <form>
                    <group>
                        <fieldname="o2m">
                            <treeeditable="bottom">
                                <fieldname="display_name"/>
                                <fieldname="text"/>
                            </tree>
                        </field>
                        <fieldname="m2m">
                            <treeeditable="bottom">
                                <fieldname="display_name"/>
                                <fieldname="text"/>
                            </tree>
                        </field>
                    </group>
                </form>`,
            res_id:1,
        });

        constth=form.el.getElementsByTagName('th')[0];
        constresizeHandle=th.getElementsByClassName('o_resize')[0];
        constfirstTableInitialWidth=form.el.querySelectorAll('.o_field_x2many_listtable')[0].offsetWidth;
        constsecondTableInititalWidth=form.el.querySelectorAll('.o_field_x2many_listtable')[1].offsetWidth;

        assert.strictEqual(firstTableInitialWidth,secondTableInititalWidth,
            "bothtablecolumnshavesamewidth");

        awaittestUtils.dom.dragAndDrop(resizeHandle,form.el.getElementsByTagName('th')[1],{position:"right"});

        assert.notEqual(firstTableInitialWidth,form.el.querySelectorAll('thead')[0].offsetWidth,
            "firsto2mtableisresizedandwidthoftablehaschanged");
        assert.strictEqual(secondTableInititalWidth,form.el.querySelectorAll('thead')[1].offsetWidth,
            "secondo2mtableshouldnotbeimpactedonfirsto2mingroupresized");

        form.destroy();
    });

    QUnit.test('resizecolumnwithx2manylistwithseveralfieldsinformnotebook',asyncfunction(assert){
        assert.expect(1);

        this.data.foo.records[0].o2m=[1,2];

        constform=awaitcreateView({
            View:FormView,
            model:'foo',
            data:this.data,
            arch:`
                <form>
                    <sheet>
                        <notebook>
                            <pagestring="Page1">
                                <fieldname="o2m">
                                    <treeeditable="bottom">
                                        <fieldname="display_name"/>
                                        <fieldname="display_name"/>
                                        <fieldname="display_name"/>
                                        <fieldname="display_name"/>
                                    </tree>
                                </field>
                            </page>
                        </notebook>
                    </sheet>
                </form>`,
            res_id:1,
        });

        constth=form.el.getElementsByTagName('th')[0];
        constresizeHandle=th.getElementsByClassName('o_resize')[0];
        constlistInitialWidth=form.el.querySelector('.o_list_view').offsetWidth;

        awaittestUtils.dom.dragAndDrop(resizeHandle,form.el.getElementsByTagName('th')[1],{position:"right"});

        assert.strictEqual(form.el.querySelector('.o_list_view').offsetWidth,listInitialWidth,
            "resizingthecolumnshouldnotimpactthewidthoflist");

        form.destroy();
    });

    QUnit.test('entereditionineditablelistwith<widget>',asyncfunction(assert){
        assert.expect(1);

        varMyWidget=Widget.extend({
            start:function(){
                this.$el.html('<iclass="fafa-info"/>');
            },
        });
        widgetRegistry.add('some_widget',MyWidget);

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<treeeditable="top">'+
                    '<widgetname="some_widget"/>'+
                    '<fieldname="int_field"/>'+
                    '<fieldname="qux"/>'+
                '</tree>',
        });

        //clickonint_fieldcelloffirstrow
        awaittestUtils.dom.click(list.$('.o_data_row:first.o_data_cell:nth(1)'));
        assert.strictEqual(document.activeElement.name,"int_field");

        list.destroy();
        deletewidgetRegistry.map.test;
    });

    QUnit.test('entereditionineditablelistwithmulti_edit=0',asyncfunction(assert){
        assert.expect(1);

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<treeeditable="top"multi_edit="0">'+
                '<fieldname="int_field"/>'+
                '</tree>',
        });

        //clickonint_fieldcelloffirstrow
        awaittestUtils.dom.click(list.$('.o_data_row:first.o_data_cell:nth(0)'));
        assert.strictEqual(document.activeElement.name,"int_field");

        list.destroy();
    });

    QUnit.test('entereditionineditablelistwithmulti_edit=1',asyncfunction(assert){
        assert.expect(1);

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<treeeditable="top"multi_edit="1">'+
                '<fieldname="int_field"/>'+
                '</tree>',
        });

        //clickonint_fieldcelloffirstrow
        awaittestUtils.dom.click(list.$('.o_data_row:first.o_data_cell:nth(0)'));
        assert.strictEqual(document.activeElement.name,"int_field");

        list.destroy();
    });

    QUnit.test('listviewwithfieldcomponent:mountedandwillUnmountcalls',asyncfunction(assert){
        //thistestcouldberemovedassoonasthelistviewwillbewritteninOwl
        assert.expect(7);

        letmountedCalls=0;
        letwillUnmountCalls=0;
        classMyFieldextendsAbstractFieldOwl{
            mounted(){
                mountedCalls++;
            }
            willUnmount(){
                willUnmountCalls++;
            }
        }
        MyField.template=owl.tags.xml`<span>HelloWorld</span>`;
        fieldRegistryOwl.add('my_owl_field',MyField);

        constlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<tree><fieldname="foo"widget="my_owl_field"/></tree>',
        });

        assert.containsN(list,'.o_data_row',4);
        assert.strictEqual(mountedCalls,4);
        assert.strictEqual(willUnmountCalls,0);

        awaitlist.reload();
        assert.strictEqual(mountedCalls,8);
        assert.strictEqual(willUnmountCalls,4);

        list.destroy();
        assert.strictEqual(mountedCalls,8);
        assert.strictEqual(willUnmountCalls,8);
    });

    QUnit.test('editablelistview:multieditionofowlfieldcomponent',asyncfunction(assert){
        //thistestcouldberemovedassoonasallfieldwidgetswillbewritteninowl
        assert.expect(5);

        constlist=awaitcreateView({
            arch:'<treemulti_edit="1"><fieldname="bar"/></tree>',
            data:this.data,
            model:'foo',
            View:ListView,
        });

        assert.containsN(list,'.o_data_row',4);
        assert.containsN(list,'.o_data_cell.custom-checkboxinput:checked',3);

        //selectallrecordsandeditthebooleanfield
        awaittestUtils.dom.click(list.$('thead.o_list_record_selectorinput'));
        assert.containsN(list,'.o_data_row.o_list_record_selectorinput:checked',4);
        awaittestUtils.dom.click(list.$('.o_data_cell:first'));
        awaittestUtils.dom.click(list.$('.o_data_cell.o_field_booleaninput'));

        assert.containsOnce(document.body,'.modal');
        awaittestUtils.dom.click($('.modal.modal-footer.btn-primary'));

        assert.containsNone(list,'.o_data_cell.custom-checkboxinput:checked');

        list.destroy();
    });

    QUnit.test("Dateinevaluationcontextworkswithdatefield",asyncfunction(assert){
        assert.expect(11);

        constdateRegex=/^\d{4}-\d{2}-\d{2}$/;
        constunpatchDate=testUtils.mock.patchDate(1997,0,9,12,0,0);
        testUtils.mock.patch(BasicModel,{
            _getEvalContext(){
                constevalContext=this._super(...arguments);
                assert.ok(dateRegex.test(evalContext.today));
                assert.strictEqual(evalContext.current_date,evalContext.today);
                returnevalContext;
            },
        });

        this.data.foo.fields.birthday={string:"Birthday",type:'date'};
        this.data.foo.records[0].birthday="1997-01-08";
        this.data.foo.records[1].birthday="1997-01-09";
        this.data.foo.records[2].birthday="1997-01-10";

        constlist=awaitcreateView({
            arch:`
                <tree>
                    <fieldname="birthday"decoration-danger="birthday>today"/>
                </tree>`,
            data:this.data,
            model:'foo',
            View:ListView,
        });

        assert.containsOnce(list,".o_data_row.text-danger");

        list.destroy();
        unpatchDate();
        testUtils.mock.unpatch(BasicModel);
    });

    QUnit.test("Datetimeinevaluationcontextworkswithdatetimefield",asyncfunction(assert){
        assert.expect(6);

        constdatetimeRegex=/^\d{4}-\d{2}-\d{2}\d{2}:\d{2}:\d{2}$/;
        constunpatchDate=testUtils.mock.patchDate(1997,0,9,12,0,0);
        testUtils.mock.patch(BasicModel,{
            _getEvalContext(){
                constevalContext=this._super(...arguments);
                assert.ok(datetimeRegex.test(evalContext.now));
                returnevalContext;
            },
        });

        /**
         *Returns"1997-01-DDHH:MM:00"withD,HandMholdingcurrentUTCvalues
         *frompatcheddate+(deltaMinutes)minutes.
         *ThisisdonetoallowtestingfromanytimezonesinceUTCvaluesare
         *calculatedwiththeoffsetofthecurrentbrowser.
         */
        functiondateStringDelta(deltaMinutes){
            constd=newDate(Date.now()+1000*60*deltaMinutes);
            return`1997-01-${
                String(d.getUTCDate()).padStart(2,'0')
            }${
                String(d.getUTCHours()).padStart(2,'0')
            }:${
                String(d.getUTCMinutes()).padStart(2,'0')
            }:00`;
        }

        //"datetime"fieldmaycollidewith"datetime"objectincontext
        this.data.foo.fields.birthday={string:"Birthday",type:'datetime'};
        this.data.foo.records[0].birthday=dateStringDelta(-30);
        this.data.foo.records[1].birthday=dateStringDelta(0);
        this.data.foo.records[2].birthday=dateStringDelta(+30);

        constlist=awaitcreateView({
            arch:`
                <tree>
                    <fieldname="birthday"decoration-danger="birthday>now"/>
                </tree>`,
            data:this.data,
            model:'foo',
            View:ListView,
        });

        assert.containsOnce(list,".o_data_row.text-danger");

        list.destroy();
        unpatchDate();
        testUtils.mock.unpatch(BasicModel);
    });

    QUnit.test("updatecontrolpanelwhilelistviewismounting",asyncfunction(assert){
        constControlPanel=require('web.ControlPanel');
        constListController=require('web.ListController');

        letmountedCounterCall=0;

        ControlPanel.patch('test.ControlPanel',T=>{
            classControlPanelPatchTestextendsT{
                mounted(){
                    mountedCounterCall=mountedCounterCall+1;
                    assert.step(`mountedCounterCall-${mountedCounterCall}`);
                    super.mounted(...arguments);
                }
            }
            returnControlPanelPatchTest;
        });

        constMyListView=ListView.extend({
            config:Object.assign({},ListView.prototype.config,{
                Controller:ListController.extend({
                    asyncstart(){
                        awaitthis._super(...arguments);
                        this.renderer._updateSelection();
                    },
                }),
            }),
        });

        assert.expect(2);

        constlist=awaitcreateView({
            View:MyListView,
            model:'event',
            data:this.data,
            arch:'<tree><fieldname="name"/></tree>',
        });

        assert.verifySteps([
            'mountedCounterCall-1',
        ]);

        ControlPanel.unpatch('test.ControlPanel');

        list.destroy();
    });

    QUnit.test('edition,thennavigationwithtab(withareadonlyre-evaluatedfieldandonchange)',asyncfunction(assert){
        //Thistestmakessurethatifwehaveacellinarowthatwillbecome
        //read-onlyaftereditinganothercell,incasethekeyboardnavigation
        //moveoveritbeforeitbecomesread-onlyandthereareunsavedchanges
        //(whichwilltriggeranonchange),thefocusofthenextactivable
        //fieldwillnotcrash
        assert.expect(4);

        this.data.bar.onchanges={
            o2m:function(){},
        };
        this.data.bar.fields.o2m={string:"O2Mfield",type:"one2many",relation:"foo"};
        this.data.bar.records[0].o2m=[1,4];

        varform=awaitcreateView({
            View:FormView,
            model:'bar',
            res_id:1,
            data:this.data,
            arch:'<form>'+
                    '<group>'+
                        '<fieldname="display_name"/>'+
                        '<fieldname="o2m">'+
                            '<treeeditable="bottom">'+
                                '<fieldname="foo"/>'+
                                '<fieldname="date"attrs="{\'readonly\':[(\'foo\',\'!=\',\'yop\')]}"/>'+
                                '<fieldname="int_field"/>'+
                            '</tree>'+
                        '</field>'+
                    '</group>'+
                '</form>',
            mockRPC:function(route,args){
                if(args.method==='onchange'){
                    assert.step(args.method+':'+args.model);
                }
                returnthis._super.apply(this,arguments);
            },
            fieldDebounce:1,
            viewOptions:{
                mode:'edit',
            },
        });

        varjq_evspecial_focus_trigger=$.event.special.focus.trigger;
        //AsKeyboardEventwillbetriggeredbyJSandnotfromthe
        //User-Agentitself,thefocuseventwillnottriggerdefault
        //action(eventnotbeingtrusted),weneedtomanuallytrigger
        //'change'eventonthecurrentlyfocusedelement
        $.event.special.focus.trigger=function(){
            if(this!==document.activeElement&&this.focus){
                varactiveElement=document.activeElement;
                this.focus();
                $(activeElement).trigger('change');
            }
        };

        //editablelist,clickonfirsttdandpressTAB
        awaittestUtils.dom.click(form.$('.o_data_cell:contains(yop)'));
        assert.strictEqual(document.activeElement,form.$('tr.o_selected_rowinput[name="foo"]')[0],
            "focusshouldbeonaninputwithname=foo");
        testUtils.fields.editInput(form.$('tr.o_selected_rowinput[name="foo"]'),'newvalue');
        vartabEvent=$.Event("keydown",{which:$.ui.keyCode.TAB});
        awaittestUtils.dom.triggerEvents(form.$('tr.o_selected_rowinput[name="foo"]'),[tabEvent]);
        assert.strictEqual(document.activeElement,form.$('tr.o_selected_rowinput[name="int_field"]')[0],
            "focusshouldbeonaninputwithname=int_field");

        //RestoreoriginjQueryspecialtriggerfor'focus'
        $.event.special.focus.trigger=jq_evspecial_focus_trigger;

        assert.verifySteps(["onchange:bar"],"onchangemethodshouldhavebeencalled");
        form.destroy();
    });

    QUnit.test('selectingarowafteranotheronecontainingatablewithinanhtmlfieldshouldbethecorrectone',asyncfunction(assert){
        assert.expect(1);

        this.data.foo.fields.html={string:"HTMLfield",type:"html"}
        this.data.foo.records[0].html=`
            <tableclass="tabletable-bordered">
                <tbody>
                    <tr>
                        <td><br></td>
                        <td><br></td>
                    </tr>
                     <tr>
                        <td><br></td>
                        <td><br></td>
                    </tr>
                </tbody>
            </table>`;

        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:this.data,
            arch:'<treeeditable="top"multi_edit="1">'+
                '<fieldname="html"/>'+
                '</tree>',
        });

        awaittestUtils.dom.click(list.$('.o_data_cell:eq(1)'))
        assert.ok($('table.o_list_table>tbody>tr:eq(1)')[0].classList.contains('o_selected_row'),"Thesecondrowshouldbeselected")

        list.destroy();
    });

    QUnit.test('quicklysettingrowmodewithowl_compatibility',asyncfunction(assert){
        assert.expect(3);

        this.data.bar.fields.bool={string:'bool',type:'boolean'};
        this.data.foo.records[0].o2m=[1,2,3];

        constform=awaitcreateView({
            View:FormView,
            model:'foo',
            data:this.data,
            res_id:1,
            viewOptions:{mode:'edit'},
            arch:`<form>
                <sheet>
                    <notebook>
                        <page>
                            <fieldname="o2m">
                                <treeeditable="bottom">
                                    <fieldname="bool"/>
                                    <fieldname="display_name"/>
                                </tree>
                            </field>
                        </page>
                    </notebook>
                </sheet>
            </form>`,
        });

        awaittestUtils.dom.click(form.$('tbodytr:eq(0)td:eq(1)'));
        awaittestUtils.fields.editInput(form.$('input[name=display_name]'),'anothervalue');

        //Double-clickonafieldofthesecondrow
        testUtils.dom.click(form.$('tbodytr:eq(1)td:eq(1)'));
        testUtils.dom.click(form.$('tbodytr:eq(1)td:eq(1)'));
        awaittestUtils.nextTick();
        awaittestUtils.nextTick();

        assert.strictEqual(
            form.el.querySelector('tr:nth-child(1)>td.o_data_cell.o_field_cell.o_list_char').textContent,
            'anothervalue');

        constrows=form.$('.o_data_row.o_list_char');
        assert.containsNone(rows[0],'input');//thismeansthatthefirstrowissaved
        assert.containsOnce(rows[1],'input');//thismeansthatthesecondrowisineditmode

        form.destroy();
    });

});

});
