flectra.define('web.field_many_to_one_tests',function(require){
"usestrict";

varBasicModel=require('web.BasicModel');
varFormView=require('web.FormView');
varListView=require('web.ListView');
varrelationalFields=require('web.relational_fields');
varStandaloneFieldManagerMixin=require('web.StandaloneFieldManagerMixin');
vartestUtils=require('web.test_utils');
varWidget=require('web.Widget');

constcpHelpers=testUtils.controlPanel;
varcreateView=testUtils.createView;

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
                        display_name:{string:"PartnerType",type:"char"},
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
        },
    },function(){
        QUnit.module('FieldMany2One');

        QUnit.test('many2onesinformviews',asyncfunction(assert){
            assert.expect(5);
            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<sheet>'+
                    '<group>'+
                    '<fieldname="trululu"string="customlabel"/>'+
                    '</group>'+
                    '</sheet>'+
                    '</form>',
                archs:{
                    'partner,false,form':'<formstring="Partners"><fieldname="display_name"/></form>',
                },
                res_id:1,
                mockRPC:function(route,args){
                    if(args.method==='get_formview_action'){
                        assert.deepEqual(args.args[0],[4],"shouldcallget_formview_actionwithcorrectid");
                        returnPromise.resolve({
                            res_id:17,
                            type:'ir.actions.act_window',
                            target:'current',
                            res_model:'res.partner'
                        });
                    }
                    if(args.method==='get_formview_id'){
                        assert.deepEqual(args.args[0],[4],"shouldcallget_formview_idwithcorrectid");
                        returnPromise.resolve(false);
                    }
                    returnthis._super(route,args);
                },
            });

            testUtils.mock.intercept(form,'do_action',function(event){
                assert.strictEqual(event.data.action.res_id,17,
                    "shoulddoado_actionwithcorrectparameters");
            });

            assert.strictEqual(form.$('a.o_form_uri:contains(aaa)').length,1,
                "shouldcontainalink");
            awaittestUtils.dom.click(form.$('a.o_form_uri'));

            awaittestUtils.form.clickEdit(form);

            awaittestUtils.dom.click(form.$('.o_external_button'));
            assert.strictEqual($('.modal.modal-title').text().trim(),'Open:customlabel',
                "dialogtitleshoulddisplaythecustomstringlabel");

            //TODO:testthatwecanedittherecordinthedialog,andthat
            //thevalueiscorrectlyupdatedonclose
            form.destroy();
        });

        QUnit.test('editingamany2one,butnotchanginganything',asyncfunction(assert){
            assert.expect(2);
            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<sheet>'+
                    '<fieldname="trululu"/>'+
                    '</sheet>'+
                    '</form>',
                archs:{
                    'partner,false,form':'<formstring="Partners"><fieldname="display_name"/></form>',
                },
                res_id:1,
                mockRPC:function(route,args){
                    if(args.method==='get_formview_id'){
                        assert.deepEqual(args.args[0],[4],"shouldcallget_formview_idwithcorrectid");
                        returnPromise.resolve(false);
                    }
                    returnthis._super(route,args);
                },
                viewOptions:{
                    ids:[1,2],
                },
            });

            awaittestUtils.form.clickEdit(form);

            //clickontheexternalbutton(shoulddoanRPC)
            awaittestUtils.dom.click(form.$('.o_external_button'));
            //saveandclosemodal
            awaittestUtils.dom.click($('.modal.modal-footer.btn-primary:first'));
            //saveform
            awaittestUtils.form.clickSave(form);
            //clicknextonpager
            awaittestUtils.dom.click(form.el.querySelector('.o_pager.o_pager_next'));

            //thischecksthattheviewdidnotaskforconfirmationthatthe
            //recordisdirty
            assert.strictEqual(form.el.querySelector('.o_pager').innerText.trim(),'2/2',
                'pagershouldbeatsecondpage');
            form.destroy();
        });

        QUnit.test('contextinmany2oneanddefaultget',asyncfunction(assert){
            assert.expect(1);

            this.data.partner.fields.int_field.default=14;
            this.data.partner.fields.trululu.default=2;

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<fieldname="int_field"/>'+
                    '<fieldname="trululu" context="{\'blip\':int_field}"options=\'{"always_reload":True}\'/>'+
                    '</form>',
                mockRPC:function(route,args){
                    if(args.method==='name_get'){
                        assert.strictEqual(args.kwargs.context.blip,14,
                            'contextshouldhavebeenproperlysenttothenamegetrpc');
                    }
                    returnthis._super(route,args);
                },
            });
            form.destroy();
        });

        QUnit.test('editingamany2one(withformviewopenedwithexternalbutton)',asyncfunction(assert){
            assert.expect(1);
            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<sheet>'+
                    '<fieldname="trululu"/>'+
                    '</sheet>'+
                    '</form>',
                archs:{
                    'partner,false,form':'<formstring="Partners"><fieldname="foo"/></form>',
                },
                res_id:1,
                mockRPC:function(route,args){
                    if(args.method==='get_formview_id'){
                        returnPromise.resolve(false);
                    }
                    returnthis._super(route,args);
                },
                viewOptions:{
                    ids:[1,2],
                },
            });

            awaittestUtils.form.clickEdit(form);

            //clickontheexternalbutton(shoulddoanRPC)
            awaittestUtils.dom.click(form.$('.o_external_button'));

            awaittestUtils.fields.editInput($('.modalinput[name="foo"]'),'brandon');

            //saveandclosemodal
            awaittestUtils.dom.click($('.modal.modal-footer.btn-primary:first'));
            //saveform
            awaittestUtils.form.clickSave(form);
            //clicknextonpager
            awaittestUtils.dom.click(form.el.querySelector('.o_pager.o_pager_next'));

            //thischecksthattheviewdidnotaskforconfirmationthatthe
            //recordisdirty
            assert.strictEqual(form.el.querySelector('.o_pager').innerText.trim(),'2/2',
                'pagershouldbeatsecondpage');
            form.destroy();
        });

        QUnit.test('many2onesinformviewswithshow_address',asyncfunction(assert){
            assert.expect(4);
            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<sheet>'+
                    '<group>'+
                    '<field'+
                    'name="trululu"'+
                    'string="customlabel"'+
                    'context="{\'show_address\':1}"'+
                    'options="{\'always_reload\':True}"'+
                    '/>'+
                    '</group>'+
                    '</sheet>'+
                    '</form>',
                mockRPC:function(route,args){
                    if(args.method==='name_get'){
                        returnthis._super(route,args).then(function(result){
                            result[0][1]+='\nStreet\nCityZIP';
                            returnresult;
                        });
                    }
                    returnthis._super(route,args);
                },
                res_id:1,
            });

            assert.strictEqual(form.$('a.o_form_uri').html(),'<span>aaa</span><br><span>Street</span><br><span>CityZIP</span>',
                "inputshouldhaveamulti-linecontentinreadonlyduetoshow_address");
            awaittestUtils.form.clickEdit(form);
            assert.containsOnce(form,'button.o_external_button:visible',
                "shouldhaveanopenrecordbutton");

            testUtils.dom.click(form.$('input.o_input'));

            assert.containsOnce(form,'button.o_external_button:visible',
                "shouldstillhaveanopenrecordbutton");
            form.$('input.o_input').trigger('focusout');
            assert.strictEqual($('.modalbutton:contains(Createandedit)').length,0,
                "thereshouldnotbeaquickcreatemodal");

            form.destroy();
        });

        QUnit.test('show_addressworksinaviewembeddedinaviewofanothertype',asyncfunction(assert){
            assert.expect(1);

            this.data.turtle.records[1].turtle_trululu=2;

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<fieldname="display_name"/>'+
                    '<fieldname="turtles"/>'+
                    '</form>',
                res_id:1,
                archs:{
                    "turtle,false,form":'<formstring="T">'+
                        '<fieldname="display_name"/>'+
                        '<fieldname="turtle_trululu"context="{\'show_address\':1}"options="{\'always_reload\':True}"/>'+
                        '</form>',
                    "turtle,false,list":'<treeeditable="bottom">'+
                        '<fieldname="display_name"/>'+
                        '</tree>',
                },
                mockRPC:function(route,args){
                    if(args.method==='name_get'){
                        returnthis._super(route,args).then(function(result){
                            if(args.model==='partner'&&args.kwargs.context.show_address){
                                result[0][1]+='\nruemorgue\nparis75013';
                            }
                            returnresult;
                        });
                    }
                    returnthis._super(route,args);
                },
            });
            //clicktheturtlefield,opensamodalwiththeturtleformview
            awaittestUtils.dom.click(form.$('.o_data_row:firsttd.o_data_cell'));

            assert.strictEqual($('[name="turtle_trululu"]').text(),"secondrecordruemorgueparis75013",
                "Thepartner'saddressshouldbedisplayed");
            form.destroy();
        });

        QUnit.test('many2onedataisreloadedifthereisacontexttotakeintoaccount',asyncfunction(assert){
            assert.expect(1);

            this.data.turtle.records[1].turtle_trululu=2;

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<fieldname="display_name"/>'+
                    '<fieldname="turtles"/>'+
                    '</form>',
                res_id:1,
                archs:{
                    "turtle,false,form":'<formstring="T">'+
                        '<fieldname="display_name"/>'+
                        '<fieldname="turtle_trululu"context="{\'show_address\':1}"options="{\'always_reload\':True}"/>'+
                        '</form>',
                    "turtle,false,list":'<treeeditable="bottom">'+
                        '<fieldname="display_name"/>'+
                        '<fieldname="turtle_trululu"/>'+
                        '</tree>',
                },
                mockRPC:function(route,args){
                    if(args.method==='name_get'){
                        returnthis._super(route,args).then(function(result){
                            if(args.model==='partner'&&args.kwargs.context.show_address){
                                result[0][1]+='\nruemorgue\nparis75013';
                            }
                            returnresult;
                        });
                    }
                    returnthis._super(route,args);
                },
            });
            //clicktheturtlefield,opensamodalwiththeturtleformview
            awaittestUtils.dom.click(form.$('.o_data_row:first'));

            assert.strictEqual($('.modal[name=turtle_trululu]').text(),"secondrecordruemorgueparis75013",
                "Thepartner'saddressshouldbedisplayed");
            form.destroy();
        });

        QUnit.test('many2onesinformviewswithsearchmore',asyncfunction(assert){
            assert.expect(3);
            this.data.partner.records.push({
                id:5,
                display_name:"Partner4",
            },{
                    id:6,
                    display_name:"Partner5",
                },{
                    id:7,
                    display_name:"Partner6",
                },{
                    id:8,
                    display_name:"Partner7",
                },{
                    id:9,
                    display_name:"Partner8",
                },{
                    id:10,
                    display_name:"Partner9",
                });
            this.data.partner.fields.datetime.searchable=true;
            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<sheet>'+
                    '<group>'+
                    '<fieldname="trululu"/>'+
                    '</group>'+
                    '</sheet>'+
                    '</form>',
                archs:{
                    'partner,false,list':'<tree><fieldname="display_name"/></tree>',
                    'partner,false,search':'<search><fieldname="datetime"/></search>',
                },
                res_id:1,
            });

            awaittestUtils.form.clickEdit(form);

            awaittestUtils.fields.many2one.clickOpenDropdown('trululu');
            awaittestUtils.fields.many2one.clickItem('trululu','Search');

            assert.strictEqual($('tr.o_data_row').length,9,"shoulddisplay9records");

            awaitcpHelpers.toggleFilterMenu('.modal');
            awaitcpHelpers.toggleAddCustomFilter('.modal');
            assert.strictEqual(document.querySelector('.modal.o_generator_menu_field').value,'datetime',
                "datetimefieldshouldbeselected");
            awaitcpHelpers.applyFilter('.modal');

            assert.strictEqual($('tr.o_data_row').length,0,"shoulddisplay0records");
            form.destroy();
        });

        QUnit.test('onchangesonmany2onestriggerwheneditingrecordinformview',asyncfunction(assert){
            assert.expect(10);

            this.data.partner.onchanges.user_id=function(){};
            this.data.user.fields.other_field={string:"OtherField",type:"char"};
            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<sheet>'+
                    '<group>'+
                    '<fieldname="user_id"/>'+
                    '</group>'+
                    '</sheet>'+
                    '</form>',
                archs:{
                    'user,false,form':'<formstring="Users"><fieldname="other_field"/></form>',
                },
                res_id:1,
                mockRPC:function(route,args){
                    assert.step(args.method);
                    if(args.method==='get_formview_id'){
                        returnPromise.resolve(false);
                    }
                    if(args.method==='onchange'){
                        assert.strictEqual(args.args[1].user_id,17,
                            "onchangeistriggeredwithcorrectuser_id");
                    }
                    returnthis._super(route,args);
                },
            });

            //openthemany2oneinformviewandchangesomething
            awaittestUtils.form.clickEdit(form);
            awaittestUtils.dom.click(form.$('.o_external_button'));
            awaittestUtils.fields.editInput($('.modal-bodyinput[name="other_field"]'),'wood');

            //savethemodalandmakesureanonchangeistriggered
            awaittestUtils.dom.click($('.modal.modal-footer.btn-primary').first());
            assert.verifySteps(['read','get_formview_id','load_views','read','write','read','onchange']);

            //savethemainrecord,andcheckthatnoextrarpcsaredone(record
            //isnotdirty,onlyarelatedrecordwasmodified)
            awaittestUtils.form.clickSave(form);
            assert.verifySteps([]);
            form.destroy();
        });

        QUnit.test("many2onedoesn'ttriggerfield_changewhenbeingemptied",asyncfunction(assert){
            assert.expect(2);

            constlist=awaitcreateView({
                arch:`
                    <treemulti_edit="1">
                        <fieldname="trululu"/>
                    </tree>`,
                data:this.data,
                model:'partner',
                View:ListView,
            });

            //Selecttworecords
            awaittestUtils.dom.click(list.$('.o_data_row:eq(0).o_list_record_selectorinput'));
            awaittestUtils.dom.click(list.$('.o_data_row:eq(1).o_list_record_selectorinput'));

            awaittestUtils.dom.click(list.$('.o_data_row:first().o_data_cell:first()'));

            const$input=list.$('.o_field_widget[name=trululu]input');

            awaittestUtils.fields.editInput($input,"");
            awaittestUtils.dom.triggerEvents($input,['keyup']);

            assert.containsNone(document.body,'.modal',
                "Nosaveshouldbetriggeredwhenremovingvalue");

            awaittestUtils.fields.many2one.clickHighlightedItem('trululu');

            assert.containsOnce(document.body,'.modal',
                "Savingshouldbetriggeredwhenselectingavalue");
            awaittestUtils.dom.click($('.modal.btn-primary'));

            list.destroy();
        });

        QUnit.test("focustrackingonamany2oneinalist",asyncfunction(assert){
            assert.expect(4);

            constlist=awaitcreateView({
                arch:'<treeeditable="top"><fieldname="trululu"/></tree>',
                archs:{
                    'partner,false,form':'<formstring="Partners"><fieldname="foo"/></form>',
                },
                data:this.data,
                model:'partner',
                View:ListView,
            });

            //Selecttworecords
            awaittestUtils.dom.click(list.$('.o_data_row:eq(0).o_list_record_selectorinput'));
            awaittestUtils.dom.click(list.$('.o_data_row:eq(1).o_list_record_selectorinput'));

            awaittestUtils.dom.click(list.$('.o_data_row:first().o_data_cell:first()'));

            constinput=list.$('.o_data_row:first().o_data_cell:first()input')[0];

            assert.strictEqual(document.activeElement,input,"Inputshouldbefocusedwhenactivated");

            awaittestUtils.fields.many2one.createAndEdit('trululu',"ABC");

            //Atthispoint,ifthefocusiscorrectlyregisteredbythem2o,there
            //shouldbeonlyonemodal(the"Create"one)andnoneforsavingchanges.
            assert.containsOnce(document.body,'.modal',"Thereshouldbeonlyonemodal");

            awaittestUtils.dom.click($('.modal.btn:not(.btn-primary)'));

            assert.strictEqual(document.activeElement,input,"Inputshouldbefocusedafterdialogcloses");
            assert.strictEqual(input.value,"","Inputshouldbeemptyafterdiscard");

            list.destroy();
        });

        QUnit.test('many2onefieldswithoption"no_open"',asyncfunction(assert){
            assert.expect(3);

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<sheet>'+
                    '<group>'+
                    '<fieldname="trululu"options="{&quot;no_open&quot;:True}"/>'+
                    '</group>'+
                    '</sheet>'+
                    '</form>',
                res_id:1,
            });

            assert.containsOnce(form,'span.o_field_widget[name=trululu]',
                "shouldbedisplayedinsideaspan(sanitycheck)");
            assert.containsNone(form,'span.o_form_uri',"shouldnothaveananchor");

            awaittestUtils.form.clickEdit(form);
            assert.containsNone(form,'.o_field_widget[name=trululu].o_external_button',"shouldnothavethebuttontoopentherecord");

            form.destroy();
        });

        QUnit.test('emptymany2onefield',asyncfunction(assert){
            assert.expect(4);

            constform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:`<formstring="Partners">
                        <sheet>
                            <group>
                                <fieldname="trululu"/>
                            </group>
                        </sheet>
                    </form>`,
                viewOptions:{
                    mode:'edit',
                },
            });

            const$dropdown=form.$('.o_field_many2oneinput').autocomplete('widget');
            awaittestUtils.fields.many2one.clickOpenDropdown('trululu');
            assert.containsNone($dropdown,'li.o_m2o_dropdown_option',
                'autocompleteshouldnotcontainsdropdownoptions');
            assert.containsOnce($dropdown,'li.o_m2o_start_typing',
                'autocompleteshouldcontainsstarttypingoption');

            awaittestUtils.fields.editAndTrigger(form.$('.o_field_many2one[name="trululu"]input'),
                'abc','keydown');
            awaittestUtils.nextTick();
            assert.containsN($dropdown,'li.o_m2o_dropdown_option',2,
                'autocompleteshouldcontains2dropdownoptions');
            assert.containsNone($dropdown,'li.o_m2o_start_typing',
                'autocompleteshouldnotcontainsstarttypingoption');

            form.destroy();
        });

        QUnit.test('emptymany2onefieldwithnodeoptions',asyncfunction(assert){
            assert.expect(2);

            constform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:`<formstring="Partners">
                    <sheet>
                        <group>
                            <fieldname="trululu"options="{'no_create_edit':1}"/>
                            <fieldname="product_id"options="{'no_create_edit':1,'no_quick_create':1}"/>
                        </group>
                    </sheet>
                </form>`,
                viewOptions:{
                    mode:'edit',
                },
            });

            const$dropdownTrululu=form.$('.o_field_many2one[name="trululu"]input').autocomplete('widget');
            const$dropdownProduct=form.$('.o_field_many2one[name="product_id"]input').autocomplete('widget');
            awaittestUtils.fields.many2one.clickOpenDropdown('trululu');
            assert.containsOnce($dropdownTrululu,'li.o_m2o_start_typing',
                'autocompleteshouldcontainsstarttypingoption');

            awaittestUtils.fields.many2one.clickOpenDropdown('product_id');
            assert.containsNone($dropdownProduct,'li.o_m2o_start_typing',
                'autocompleteshouldcontainsstarttypingoption');

            form.destroy();
        });

        QUnit.test('many2oneineditmode',asyncfunction(assert){
            assert.expect(17);

            //create10partnerstohavethe'SearchMore'optionintheautocompletedropdown
            for(vari=0;i<10;i++){
                varid=20+i;
                this.data.partner.records.push({id:id,display_name:"Partner"+id});
            }

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<sheet>'+
                    '<group>'+
                    '<fieldname="trululu"/>'+
                    '</group>'+
                    '</sheet>'+
                    '</form>',
                res_id:1,
                archs:{
                    'partner,false,list':'<treestring="Partners"><fieldname="display_name"/></tree>',
                    'partner,false,search':'<searchstring="Partners">'+
                        '<fieldname="display_name"string="Name"/>'+
                        '</search>',
                },
                mockRPC:function(route,args){
                    if(route==='/web/dataset/call_kw/partner/write'){
                        assert.strictEqual(args.args[1].trululu,20,"shouldwritethecorrectid");
                    }
                    returnthis._super.apply(this,arguments);
                },
            });

            //theSelectCreateDialogrequeststhesession,sointerceptitscustom
            //eventtospecifyafakesessiontopreventitfromcrashing
            testUtils.mock.intercept(form,'get_session',function(event){
                event.data.callback({user_context:{}});
            });

            awaittestUtils.form.clickEdit(form);

            var$dropdown=form.$('.o_field_many2oneinput').autocomplete('widget');

            awaittestUtils.fields.many2one.clickOpenDropdown('trululu');
            assert.ok($dropdown.is(':visible'),
                'clickingonthem2oinputshouldopenthedropdownifitisnotopenyet');
            assert.strictEqual($dropdown.find('li:not(.o_m2o_dropdown_option)').length,7,
                'autocompleteshouldcontains8suggestions');
            assert.strictEqual($dropdown.find('li.o_m2o_dropdown_option').length,1,
                'autocompleteshouldcontain"SearchMore"');
            assert.containsNone($dropdown,'li.o_m2o_start_typing',
                'autocompleteshouldnotcontainsstarttypingoptionifvalueisavailable');

            awaittestUtils.fields.many2one.clickOpenDropdown('trululu');
            assert.ok(!$dropdown.is(':visible'),
                'clickingonthem2oinputshouldclosethedropdownifitisopen');

            //changethevalueofthem2owithasuggestionofthedropdown
            awaittestUtils.fields.many2one.clickOpenDropdown('trululu');
            awaittestUtils.fields.many2one.clickHighlightedItem('trululu');
            assert.ok(!$dropdown.is(':visible'),'clickingonavalueshouldclosethedropdown');
            assert.strictEqual(form.$('.o_field_many2oneinput').val(),'firstrecord',
                'valueofthem2oshouldhavebeencorrectlyupdated');

            //changethevalueofthem2owitharecordinthe'SearchMore'modal
            awaittestUtils.fields.many2one.clickOpenDropdown('trululu');
            //clickon'SearchMore'(mouseenterrequiredbyui-autocomplete)
            awaittestUtils.fields.many2one.clickItem('trululu','Search');
            assert.ok($('.modal.o_list_view').length,"shouldhaveopenedalistviewinamodal");
            assert.ok(!$('.modal.o_list_view.o_list_record_selector').length,
                "thereshouldbenorecordselectorinthelistview");
            assert.ok(!$('.modal.modal-footer.o_select_button').length,
                "thereshouldbeno'Select'buttoninthefooter");
            assert.ok($('.modaltbodytr').length>10,"listshouldcontainmorethan10records");
            awaitcpHelpers.editSearch('.modal',"P");
            awaitcpHelpers.validateSearch('.modal');
            assert.strictEqual($('.modaltbodytr').length,10,
                "listshouldberestrictedtorecordscontainingaP(10records)");
            //choosearecord
            awaittestUtils.dom.click($('.modaltbodytr:contains(Partner20)'));
            assert.ok(!$('.modal').length,"shouldhaveclosedthemodal");
            assert.ok(!$dropdown.is(':visible'),'shouldhaveclosedthedropdown');
            assert.strictEqual(form.$('.o_field_many2oneinput').val(),'Partner20',
                'valueofthem2oshouldhavebeencorrectlyupdated');

            //save
            awaittestUtils.form.clickSave(form);
            assert.strictEqual(form.$('a.o_form_uri').text(),'Partner20',
                "shoulddisplaycorrectvalueaftersave");

            form.destroy();
        });

        QUnit.test('many2oneinnoneditmode',asyncfunction(assert){
            assert.expect(3);

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<fieldname="trululu"/>'+
                    '</form>',
                res_id:1,
            });

            assert.containsOnce(form,'a.o_form_uri',
                "shoulddisplay1m2olinkinform");
            assert.hasAttrValue(form.$('a.o_form_uri'),'href',"#id=4&model=partner",
                "hrefshouldcontainidandmodel");

            //Removevaluefrommany2oneandthensave,thereshouldnothavehrefwithidandmodelonm2oanchor
            awaittestUtils.form.clickEdit(form);
            form.$('.o_field_many2oneinput').val('').trigger('keyup').trigger('focusout');
            awaittestUtils.form.clickSave(form);

            assert.hasAttrValue(form.$('a.o_form_uri'),'href',"#",
                "hrefshouldhave#");

            form.destroy();
        });

        QUnit.test('many2onewithco-modelwhosenamefieldisamany2one',asyncfunction(assert){
            assert.expect(4);

            this.data.product.fields.name={
                string:'UserName',
                type:'many2one',
                relation:'user',
            };

            constform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<form><fieldname="product_id"/></form>',
                archs:{
                    'product,false,form':'<form><fieldname="name"/></form>',
                },
            });

            awaittestUtils.fields.many2one.createAndEdit('product_id',"ABC");
            assert.containsOnce(document.body,'.modal.o_form_view');

            //quickcreate'newvalue'
            awaittestUtils.fields.many2one.searchAndClickItem('name',{search:'newvalue'});
            assert.strictEqual($('.modal.o_field_many2oneinput').val(),'newvalue');

            awaittestUtils.dom.click($('.modal.modal-footer.btn-primary'));//saveinmodal
            assert.containsNone(document.body,'.modal.o_form_view');
            assert.strictEqual(form.$('.o_field_many2oneinput').val(),'newvalue');

            form.destroy();
        });

        QUnit.test('many2onesearcheswithcorrectvalue',asyncfunction(assert){
            assert.expect(6);

            varM2O_DELAY=relationalFields.FieldMany2One.prototype.AUTOCOMPLETE_DELAY;
            relationalFields.FieldMany2One.prototype.AUTOCOMPLETE_DELAY=0;

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<sheet>'+
                    '<fieldname="trululu"/>'+
                    '</sheet>'+
                    '</form>',
                res_id:1,
                mockRPC:function(route,args){
                    if(args.method==='name_search'){
                        assert.step('search:'+args.kwargs.name);
                    }
                    returnthis._super.apply(this,arguments);
                },
                viewOptions:{
                    mode:'edit',
                },
            });

            assert.strictEqual(form.$('.o_field_many2oneinput').val(),'aaa',
                "shouldbeinitiallysetto'aaa'");

            awaittestUtils.dom.click(form.$('.o_field_many2oneinput'));
            //unsetthemany2one->shouldsearchagainwith''
            form.$('.o_field_many2oneinput').val('').trigger('keydown');
            awaittestUtils.nextTick();
            form.$('.o_field_many2oneinput').val('p').trigger('keydown').trigger('keyup');
            awaittestUtils.nextTick();

            //closeandre-openthedropdown->shouldsearchwith'p'again
            awaittestUtils.dom.click(form.$('.o_field_many2oneinput'));
            awaittestUtils.dom.click(form.$('.o_field_many2oneinput'));

            assert.verifySteps(['search:','search:','search:p','search:p']);

            relationalFields.FieldMany2One.prototype.AUTOCOMPLETE_DELAY=M2O_DELAY;
            form.destroy();
        });

        QUnit.test('many2onesearchwithtrailingandleadingspaces',asyncfunction(assert){
            assert.expect(10);

            constform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:`<form><fieldname="trululu"/></form>`,
                mockRPC:function(route,args){
                    if(args.method==='name_search'){
                        assert.step('search:'+args.kwargs.name);
                    }
                    returnthis._super.apply(this,arguments);
                },
            });

            const$dropdown=form.$('.o_field_many2oneinput').autocomplete('widget');

            awaittestUtils.fields.many2one.clickOpenDropdown('trululu');
            assert.isVisible($dropdown);
            assert.containsN($dropdown,'li:not(.o_m2o_dropdown_option)',4,
                'autocompleteshouldcontains4suggestions');

            //searchwithleadingspaces
            form.$('.o_field_many2oneinput').val('  first').trigger('keydown').trigger('keyup');
            awaittestUtils.nextTick();
            assert.containsOnce($dropdown,'li:not(.o_m2o_dropdown_option)',
                'autocompleteshouldcontains1suggestion');

            //searchwithtrailingspaces
            form.$('.o_field_many2oneinput').val('first ').trigger('keydown').trigger('keyup');
            awaittestUtils.nextTick();
            assert.containsOnce($dropdown,'li:not(.o_m2o_dropdown_option)',
                'autocompleteshouldcontains1suggestion');

            //searchwithleadingandtrailingspaces
            form.$('.o_field_many2oneinput').val('  first  ').trigger('keydown').trigger('keyup');
            awaittestUtils.nextTick();
            assert.containsOnce($dropdown,'li:not(.o_m2o_dropdown_option)',
                'autocompleteshouldcontains1suggestion');

            assert.verifySteps(['search:','search:first','search:first','search:first']);

            form.destroy();
        });

        QUnit.test('many2onefieldwithoptionalways_reload',asyncfunction(assert){
            assert.expect(4);
            varcount=0;
            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<form>'+
                    '<fieldname="trululu"options="{\'always_reload\':True}"/>'+
                    '</form>',
                res_id:2,
                mockRPC:function(route,args){
                    if(args.method==='name_get'){
                        count++;
                        returnPromise.resolve([[1,"firstrecord\nandsomeaddress"]]);
                    }
                    returnthis._super(route,args);
                },
            });

            assert.strictEqual(count,1,"anextraname_getshouldhavebeendone");
            assert.ok(form.$('a:contains(andsomeaddress)').length,
                "shoulddisplayadditionalresult");

            awaittestUtils.form.clickEdit(form);

            assert.strictEqual(form.$('.o_field_widget[name=trululu]input').val(),"firstrecord",
                "actualfieldvalueshouldbedisplayedtobeedited");

            awaittestUtils.form.clickSave(form);

            assert.ok(form.$('a:contains(andsomeaddress)').length,
                "shouldstilldisplayadditionalresult");
            form.destroy();
        });

        QUnit.test('many2onefieldandlistnavigation',asyncfunction(assert){
            assert.expect(3);

            varlist=awaitcreateView({
                View:ListView,
                model:'partner',
                data:this.data,
                arch:'<treeeditable="bottom"><fieldname="trululu"/></tree>',
            });

            //editfirstinput,totriggerautocomplete
            awaittestUtils.dom.click(list.$('.o_data_row.o_data_cell').first());
            awaittestUtils.fields.editInput(list.$('.o_data_cellinput'),'');

            //presskeydown,toselectfirstchoice
            awaittestUtils.fields.triggerKeydown(list.$('.o_data_cellinput').focus(),'down');

            //wenowcheckthatthedropdownisopen(andthatthefocusdidnotgo
            //tothenextline)
            var$dropdown=list.$('.o_field_many2oneinput').autocomplete('widget');
            assert.ok($dropdown.is(':visible'),"dropdownshouldbevisible");
            assert.hasClass(list.$('.o_data_row:eq(0)'),'o_selected_row',
                'firstdatarowshouldstillbeselected');
            assert.doesNotHaveClass(list.$('.o_data_row:eq(1)'),'o_selected_row',
                'seconddatarowshouldnotbeselected');

            list.destroy();
        });

        QUnit.test('standalonemany2onefield',asyncfunction(assert){
            assert.expect(4);

            varM2O_DELAY=relationalFields.FieldMany2One.prototype.AUTOCOMPLETE_DELAY;
            relationalFields.FieldMany2One.prototype.AUTOCOMPLETE_DELAY=0;

            varfixture=$('#qunit-fixture');
            varself=this;

            varmodel=awaittestUtils.createModel({
                Model:BasicModel,
                data:this.data,
            });
            varrecord;
            model.makeRecord('coucou',[{
                name:'partner_id',
                relation:'partner',
                type:'many2one',
                value:[1,'firstpartner'],
            }]).then(function(recordID){
                record=model.get(recordID);
            });
            awaittestUtils.nextTick();
            //createanewwidgetthatusestheStandaloneFieldManagerMixin
            varStandaloneWidget=Widget.extend(StandaloneFieldManagerMixin,{
                init:function(parent){
                    this._super.apply(this,arguments);
                    StandaloneFieldManagerMixin.init.call(this,parent);
                },
            });
            varparent=newStandaloneWidget(model);
            model.setParent(parent);
            awaittestUtils.mock.addMockEnvironment(parent,{
                data:self.data,
                mockRPC:function(route,args){
                    assert.step(args.method);
                    returnthis._super.apply(this,arguments);
                },
            });

            varrelField=newrelationalFields.FieldMany2One(parent,'partner_id',record,{
                mode:'edit',
                noOpen:true,
            });

            relField.appendTo(fixture);
            awaittestUtils.nextTick();
            awaittestUtils.fields.editInput($('input.o_input'),'xyzzrot');

            awaittestUtils.fields.many2one.clickItem('partner_id','Create');

            assert.containsNone(relField,'.o_external_button',
                "shouldnothavethebuttontoopentherecord");
            assert.verifySteps(['name_search','name_create']);

            parent.destroy();
            model.destroy();
            relationalFields.FieldMany2One.prototype.AUTOCOMPLETE_DELAY=M2O_DELAY;
        });

        //QUnit.test('onchangeonamany2onetoadifferentmodel',asyncfunction(assert){
        //Thistestiscommentedbecausethemockserverdoesnotgivethecorrectresponse.
        //Itshouldreturnacouple[id,display_name],butIdon'tknowthelogicused
        //bytheserver,soit'shardtoemulateitcorrectly
        //    assert.expect(2);

        //    this.data.partner.records[0].product_id=41;
        //    this.data.partner.onchanges={
        //        foo:function(obj){
        //            obj.product_id=37;
        //        },
        //    };

        //    varform=awaitcreateView({
        //        View:FormView,
        //        model:'partner',
        //        data:this.data,
        //        arch:'<form>'+
        //                '<fieldname="foo"/>'+
        //                '<fieldname="product_id"/>'+
        //            '</form>',
        //        res_id:1,
        //    });
        //    awaittestUtils.form.clickEdit(form);
        //    assert.strictEqual(form.$('input').eq(1).val(),'xpad',"initialproduct_idvalshouldbexpad");

        //    testUtils.fields.editInput(form.$('input').eq(0),"letustriggeranonchange");

        //    assert.strictEqual(form.$('input').eq(1).val(),'xphone',"onchangeshouldhavebeenapplied");
        //});

        QUnit.test('form:quickcreatethensavedirectly',asyncfunction(assert){
            assert.expect(5);

            varprom=testUtils.makeTestPromise();
            varnewRecordID;
            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<form>'+
                    '<fieldname="trululu"/>'+
                    '</form>',
                mockRPC:function(route,args){
                    varresult=this._super.apply(this,arguments);
                    if(args.method==='name_create'){
                        assert.step('name_create');
                        returnprom.then(_.constant(result)).then(function(nameGet){
                            newRecordID=nameGet[0];
                            returnnameGet;
                        });
                    }
                    if(args.method==='create'){
                        assert.step('create');
                        assert.strictEqual(args.args[0].trululu,newRecordID,
                            "shouldcreatewiththecorrectm2oid");
                    }
                    returnresult;
                },
            });
            awaittestUtils.fields.many2one.searchAndClickItem('trululu',{search:'b'});
            awaittestUtils.form.clickSave(form);

            assert.verifySteps(['name_create'],
                "shouldwaitforthename_createbeforecreatingtherecord");

            awaitprom.resolve();
            awaittestUtils.nextTick();

            assert.verifySteps(['create']);
            form.destroy();
        });

        QUnit.test('form:quickcreateforfieldthatreturnsfalseaftername_createcall',asyncfunction(assert){
            assert.expect(3);
            constform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<form><fieldname="trululu"/></form>',
                mockRPC:function(route,args){
                    constresult=this._super.apply(this,arguments);
                    if(args.method==='name_create'){
                        assert.step('name_create');
                        //Resolvethename_createcalltofalse.Thisispossibleif
                        //_rec_nameforthemodelofthefieldisunassigned.
                        returnPromise.resolve(false);
                    }
                    returnresult;
                },
            });
            awaittestUtils.fields.many2one.searchAndClickItem('trululu',{search:'beam'});
            assert.verifySteps(['name_create'],'attempttoname_create');
            assert.strictEqual(form.$(".o_input_dropdowninput").val(),"",
                "theinputshouldcontainnotextaftersearchandclick")
            form.destroy();
        });

        QUnit.test('list:quickcreatethensavedirectly',asyncfunction(assert){
            assert.expect(8);

            varprom=testUtils.makeTestPromise();
            varnewRecordID;
            varlist=awaitcreateView({
                View:ListView,
                model:'partner',
                data:this.data,
                arch:'<treeeditable="top">'+
                    '<fieldname="trululu"/>'+
                    '</tree>',
                mockRPC:function(route,args){
                    varresult=this._super.apply(this,arguments);
                    if(args.method==='name_create'){
                        assert.step('name_create');
                        returnprom.then(_.constant(result)).then(function(nameGet){
                            newRecordID=nameGet[0];
                            returnnameGet;
                        });
                    }
                    if(args.method==='create'){
                        assert.step('create');
                        assert.strictEqual(args.args[0].trululu,newRecordID,
                            "shouldcreatewiththecorrectm2oid");
                    }
                    returnresult;
                },
            });

            awaittestUtils.dom.click(list.$buttons.find('.o_list_button_add'));

            awaittestUtils.fields.many2one.searchAndClickItem('trululu',{search:'b'});
            list.$buttons.find('.o_list_button_add').show();
            testUtils.dom.click(list.$buttons.find('.o_list_button_add'));

            assert.verifySteps(['name_create'],
                "shouldwaitforthename_createbeforecreatingtherecord");
            assert.containsN(list,'.o_data_row',4,
                "shouldwaitforthename_createbeforeaddingthenewrow");

            awaitprom.resolve();
            awaittestUtils.nextTick();

            assert.verifySteps(['create']);
            assert.strictEqual(list.$('.o_data_row:nth(1).o_data_cell').text(),'b',
                "createdrowshouldhavethecorrectm2ovalue");
            assert.containsN(list,'.o_data_row',5,"shouldhaveaddedthefifthrow");

            list.destroy();
        });

        QUnit.test('listinform:quickcreatethensavedirectly',asyncfunction(assert){
            assert.expect(6);

            varprom=testUtils.makeTestPromise();
            varnewRecordID;
            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<form>'+
                    '<sheet>'+
                    '<fieldname="p">'+
                    '<treeeditable="bottom">'+
                    '<fieldname="trululu"/>'+
                    '</tree>'+
                    '</field>'+
                    '</sheet>'+
                    '</form>',
                mockRPC:function(route,args){
                    varresult=this._super.apply(this,arguments);
                    if(args.method==='name_create'){
                        assert.step('name_create');
                        returnprom.then(_.constant(result)).then(function(nameGet){
                            newRecordID=nameGet[0];
                            returnnameGet;
                        });
                    }
                    if(args.method==='create'){
                        assert.step('create');
                        assert.strictEqual(args.args[0].p[0][2].trululu,newRecordID,
                            "shouldcreatewiththecorrectm2oid");
                    }
                    returnresult;
                },
            });

            awaittestUtils.dom.click(form.$('.o_field_x2many_list_row_adda'));
            awaittestUtils.fields.many2one.searchAndClickItem('trululu',{search:'b'});
            awaittestUtils.form.clickSave(form);

            assert.verifySteps(['name_create'],
                "shouldwaitforthename_createbeforecreatingtherecord");

            awaitprom.resolve();
            awaittestUtils.nextTick();

            assert.verifySteps(['create']);
            assert.strictEqual(form.$('.o_data_row:first.o_data_cell').text(),'b',
                "firstrowshouldhavethecorrectm2ovalue");
            form.destroy();
        });

        QUnit.test('listinform:quickcreatethenaddanewlinedirectly',asyncfunction(assert){
            //requiredmany2oneinsideaone2manylist:directlyafterquickcreating
            //anewmany2onevalue(beforethename_createreturns),clickonaddanitem:
            //atthismoment,themany2onehasstillnovalue,andasitisrequired,
            //therowisdiscardedifasaveLineisrequested.However,itshould
            //waitforthename_createtoreturnbeforetryingtosavetheline.
            assert.expect(8);

            this.data.partner.onchanges={
                trululu:function(){},
            };

            varM2O_DELAY=relationalFields.FieldMany2One.prototype.AUTOCOMPLETE_DELAY;
            relationalFields.FieldMany2One.prototype.AUTOCOMPLETE_DELAY=0;

            varprom=testUtils.makeTestPromise();
            varnewRecordID;
            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<form>'+
                    '<sheet>'+
                    '<fieldname="p">'+
                    '<treeeditable="bottom">'+
                    '<fieldname="trululu"required="1"/>'+
                    '</tree>'+
                    '</field>'+
                    '</sheet>'+
                    '</form>',
                mockRPC:function(route,args){
                    varresult=this._super.apply(this,arguments);
                    if(args.method==='name_create'){
                        returnprom.then(_.constant(result)).then(function(nameGet){
                            newRecordID=nameGet[0];
                            returnnameGet;
                        });
                    }
                    if(args.method==='create'){
                        assert.deepEqual(args.args[0].p[0][2].trululu,newRecordID);
                    }
                    returnresult;
                },
            });

            awaittestUtils.dom.click(form.$('.o_field_x2many_list_row_adda'));
            awaittestUtils.fields.editAndTrigger(form.$('.o_field_many2oneinput'),
                'b','keydown');
            awaittestUtils.fields.many2one.clickHighlightedItem('trululu');
            awaittestUtils.dom.click(form.$('.o_field_x2many_list_row_adda'));

            assert.containsOnce(form,'.o_data_row',
                "thereshouldstillbeonlyonerow");
            assert.hasClass(form.$('.o_data_row'),'o_selected_row',
                "therowshouldstillbeinedition");

            awaitprom.resolve();
            awaittestUtils.nextTick();

            assert.strictEqual(form.$('.o_data_row:first.o_data_cell').text(),'b',
                "firstrowshouldhavethecorrectm2ovalue");
            assert.containsN(form,'.o_data_row',2,
                "thereshouldnowbe2rows");
            assert.hasClass(form.$('.o_data_row:nth(1)'),'o_selected_row',
                "thesecondrowshouldbeinedition");

            awaittestUtils.form.clickSave(form);

            assert.containsOnce(form,'.o_data_row',
                "thereshouldbe1rowsaved(thesecondonewasemptyandinvalid)");
            assert.strictEqual(form.$('.o_data_row.o_data_cell').text(),'b',
                "shouldhavethecorrectm2ovalue");

            relationalFields.FieldMany2One.prototype.AUTOCOMPLETE_DELAY=M2O_DELAY;
            form.destroy();
        });

        QUnit.test('listinform:createwithone2manywithmany2one',asyncfunction(assert){
            assert.expect(1);

            this.data.partner.fields.p.default=[[0,0,{display_name:'newrecord',p:[]}]];

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<form>'+
                    '<sheet>'+
                    '<fieldname="p">'+
                    '<treeeditable="bottom">'+
                    '<fieldname="display_name"/>'+
                    '<fieldname="trululu"/>'+
                    '</tree>'+
                    '</field>'+
                    '</sheet>'+
                    '</form>',
                mockRPC:function(route,args){
                    if(args.method==='name_get'){
                        thrownewError('Namegetshouldnotbecalled');
                    }
                    returnthis._super.apply(this,arguments);
                },
            });

            assert.strictEqual($('td.o_data_cell:first').text(),'newrecord',
                "shouldhavecreatedthenewrecordintheo2mwiththecorrectname");

            form.destroy();
        });

        QUnit.test('listinform:createwithone2manywithmany2one(version2)',asyncfunction(assert){
            //Thistestsimulatestheexactsamescenarioasthepreviousone,
            //exceptthatthevalueforthemany2oneisexplicitelysettofalse,
            //whichisstupid,butthishappens,sowehavetohandleit
            assert.expect(1);

            this.data.partner.fields.p.default=[
                [0,0,{display_name:'newrecord',trululu:false,p:[]}]
            ];

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<form>'+
                    '<sheet>'+
                    '<fieldname="p">'+
                    '<treeeditable="bottom">'+
                    '<fieldname="display_name"/>'+
                    '<fieldname="trululu"/>'+
                    '</tree>'+
                    '</field>'+
                    '</sheet>'+
                    '</form>',
                mockRPC:function(route,args){
                    if(args.method==='name_get'){
                        thrownewError('Namegetshouldnotbecalled');
                    }
                    returnthis._super.apply(this,arguments);
                },
            });

            assert.strictEqual($('td.o_data_cell:first').text(),'newrecord',
                "shouldhavecreatedthenewrecordintheo2mwiththecorrectname");

            form.destroy();
        });

        QUnit.test('itemnotdroppedondiscardwithemptyrequiredfield(default_get)',asyncfunction(assert){
            //Thistestsimulatesdiscardingarecordthathasbeencreatedwith
            //oneofitsrequiredfieldthatisempty.Whenwediscardthechanges
            //onthisemptyfield,itshouldnotassumethatthisrecordshouldbe
            //abandonned,sinceithasbeenadded(eventhoughitisanewrecord).
            assert.expect(8);

            this.data.partner.fields.p.default=[
                [0,0,{display_name:'newrecord',trululu:false,p:[]}]
            ];

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<form>'+
                    '<sheet>'+
                    '<fieldname="p">'+
                    '<treeeditable="bottom">'+
                    '<fieldname="display_name"/>'+
                    '<fieldname="trululu"required="1"/>'+
                    '</tree>'+
                    '</field>'+
                    '</sheet>'+
                    '</form>',
            });

            assert.strictEqual($('tr.o_data_row').length,1,
                "shouldhavecreatedthenewrecordintheo2m");
            assert.strictEqual($('td.o_data_cell').first().text(),"newrecord",
                "shouldhavethecorrectdisplayedname");

            varrequiredElement=$('td.o_data_cell.o_required_modifier');
            assert.strictEqual(requiredElement.length,1,
                "shouldhavearequiredfieldonthisrecord");
            assert.strictEqual(requiredElement.text(),"",
                "shouldhaveemptystringintherequiredfieldonthisrecord");

            testUtils.dom.click(requiredElement);
            //discardbyclickingonbody
            testUtils.dom.click($('body'));

            assert.strictEqual($('tr.o_data_row').length,1,
                "shouldstillhavetherecordintheo2m");
            assert.strictEqual($('td.o_data_cell').first().text(),"newrecord",
                "shouldstillhavethecorrectdisplayedname");

            //updateselectorofrequiredfieldelement
            requiredElement=$('td.o_data_cell.o_required_modifier');
            assert.strictEqual(requiredElement.length,1,
                "shouldstillhavetherequiredfieldonthisrecord");
            assert.strictEqual(requiredElement.text(),"",
                "shouldstillhaveemptystringintherequiredfieldonthisrecord");
            form.destroy();
        });

        QUnit.test('listinform:name_getwithuniqueids(default_get)',asyncfunction(assert){
            assert.expect(1);

            this.data.partner.records[0].display_name="MyTrululu";
            this.data.partner.fields.p.default=[
                [0,0,{trululu:1,p:[]}],
                [0,0,{trululu:1,p:[]}]
            ];

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<form>'+
                    '<sheet>'+
                    '<fieldname="p">'+
                    '<treeeditable="bottom">'+
                    '<fieldname="trululu"/>'+
                    '</tree>'+
                    '</field>'+
                    '</sheet>'+
                    '</form>',
                mockRPC:function(route,args){
                    if(args.method==='name_get'){
                        thrownewError('shouldnotcallname_get');
                    }
                    returnthis._super.apply(this,arguments);
                },
            });

            assert.strictEqual(form.$('td.o_data_cell').text(),"MyTrululuMyTrululu",
                "bothrecordsshouldhavethecorrectdisplay_namefortrululufield");

            form.destroy();
        });

        QUnit.test('listinform:shownameofmany2onefieldsinmulti-page(default_get)',asyncfunction(assert){
            assert.expect(4);

            this.data.partner.fields.p.default=[
                [0,0,{display_name:'record1',trululu:1,p:[]}],
                [0,0,{display_name:'record2',trululu:2,p:[]}]
            ];

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<form>'+
                    '<sheet>'+
                    '<fieldname="p">'+
                    '<treeeditable="bottom"limit="1">'+
                    '<fieldname="display_name"/>'+
                    '<fieldname="trululu"/>'+
                    '</tree>'+
                    '</field>'+
                    '</sheet>'+
                    '</form>',
            });

            assert.strictEqual(form.$('td.o_data_cell').first().text(),
                "record1","shouldshowdisplay_nameof1strecord");
            assert.strictEqual(form.$('td.o_data_cell').first().next().text(),
                "firstrecord","shouldshowdisplay_nameoftrululuof1strecord");

            awaittestUtils.dom.click(form.$('button.o_pager_next'));

            assert.strictEqual(form.$('td.o_data_cell').first().text(),
                "record2","shouldshowdisplay_nameof2ndrecord");
            assert.strictEqual(form.$('td.o_data_cell').first().next().text(),
                "secondrecord","shouldshowdisplay_nameoftrululuof2ndrecord");

            form.destroy();
        });

        QUnit.test('listinform:itemnotdroppedondiscardwithemptyrequiredfield(onchangeindefault_get)',asyncfunction(assert){
            //variantofthetest"listinform:discardnewlyaddedelementwith
            //emptyrequiredfield(default_get)",inwhichthe`default_get`
            //performsan`onchange`atthesametime.This`onchange`maycreate
            //somerecords,whichshouldnotbeabandonedondiscard,similarly
            //torecordscreateddirectlyby`default_get`
            assert.expect(7);

            varM2O_DELAY=relationalFields.FieldMany2One.prototype.AUTOCOMPLETE_DELAY;
            relationalFields.FieldMany2One.prototype.AUTOCOMPLETE_DELAY=0;

            this.data.partner.fields.product_id.default=37;
            this.data.partner.onchanges={
                product_id:function(obj){
                    if(obj.product_id===37){
                        obj.p=[[0,0,{display_name:"entry",trululu:false}]];
                    }
                },
            };

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<form>'+
                    '<fieldname="product_id"/>'+
                    '<fieldname="p">'+
                    '<treeeditable="bottom">'+
                    '<fieldname="display_name"/>'+
                    '<fieldname="trululu"required="1"/>'+
                    '</tree>'+
                    '</field>'+
                    '</form>',
            });

            //checkthatthereisarecordintheeditablelistwithemptystringasrequiredfield
            assert.containsOnce(form,'.o_data_row',
                "shouldhavearowintheeditablelist");
            assert.strictEqual($('td.o_data_cell').first().text(),"entry",
                "shouldhavethecorrectdisplayedname");
            varrequiredField=$('td.o_data_cell.o_required_modifier');
            assert.strictEqual(requiredField.length,1,
                "shouldhavearequiredfieldonthisrecord");
            assert.strictEqual(requiredField.text(),"",
                "shouldhaveemptystringintherequiredfieldonthisrecord");

            //clickonemptyrequiredfieldineditablelistrecord
            testUtils.dom.click(requiredField);
            //clickoffsothattherequiredfieldstillstayempty
            testUtils.dom.click($('body'));

            //recordshouldnotbedropped
            assert.containsOnce(form,'.o_data_row',
                "shouldnothavedroppedrecordintheeditablelist");
            assert.strictEqual($('td.o_data_cell').first().text(),"entry",
                "shouldstillhavethecorrectdisplayedname");
            assert.strictEqual($('td.o_data_cell.o_required_modifier').text(),"",
                "shouldstillhaveemptystringintherequiredfield");

            relationalFields.FieldMany2One.prototype.AUTOCOMPLETE_DELAY=M2O_DELAY;
            form.destroy();
        });

        QUnit.test('listinform:itemnotdroppedondiscardwithemptyrequiredfield(onchangeonlistafterdefault_get)',asyncfunction(assert){
            //discardingarecordfroman`onchange`ina`default_get`shouldnot
            //abandontherecord.Thisshouldnotbethecaseforfollowing
            //`onchange`,exceptifanonchangemakesomechangesonthelist:
            //inparticular,ifanonchangemakechangesonthelistsuchthat
            //arecordisadded,thisrecordshouldnotbedroppedondiscard
            assert.expect(8);

            varM2O_DELAY=relationalFields.FieldMany2One.prototype.AUTOCOMPLETE_DELAY;
            relationalFields.FieldMany2One.prototype.AUTOCOMPLETE_DELAY=0;

            this.data.partner.onchanges={
                product_id:function(obj){
                    if(obj.product_id===37){
                        obj.p=[[0,0,{display_name:"entry",trululu:false}]];
                    }
                },
            };

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<form>'+
                    '<fieldname="product_id"/>'+
                    '<fieldname="p">'+
                    '<treeeditable="bottom">'+
                    '<fieldname="display_name"/>'+
                    '<fieldname="trululu"required="1"/>'+
                    '</tree>'+
                    '</field>'+
                    '</form>',
            });

            //checknorecordinlist
            assert.containsNone(form,'.o_data_row',
                "shouldhavenorowintheeditablelist");

            //selectproduct_idtoforceon_changeineditablelist
            awaittestUtils.dom.click(form.$('.o_field_widget[name="product_id"].o_input'));
            awaittestUtils.dom.click($('.ui-menu-item').first());

            //checkthatthereisarecordintheeditablelistwithemptystringasrequiredfield
            assert.containsOnce(form,'.o_data_row',
                "shouldhavearowintheeditablelist");
            assert.strictEqual($('td.o_data_cell').first().text(),"entry",
                "shouldhavethecorrectdisplayedname");
            varrequiredField=$('td.o_data_cell.o_required_modifier');
            assert.strictEqual(requiredField.length,1,
                "shouldhavearequiredfieldonthisrecord");
            assert.strictEqual(requiredField.text(),"",
                "shouldhaveemptystringintherequiredfieldonthisrecord");

            //clickonemptyrequiredfieldineditablelistrecord
            awaittestUtils.dom.click(requiredField);
            //clickoffsothattherequiredfieldstillstayempty
            awaittestUtils.dom.click($('body'));

            //recordshouldnotbedropped
            assert.containsOnce(form,'.o_data_row',
                "shouldnothavedroppedrecordintheeditablelist");
            assert.strictEqual($('td.o_data_cell').first().text(),"entry",
                "shouldstillhavethecorrectdisplayedname");
            assert.strictEqual($('td.o_data_cell.o_required_modifier').text(),"",
                "shouldstillhaveemptystringintherequiredfield");

            relationalFields.FieldMany2One.prototype.AUTOCOMPLETE_DELAY=M2O_DELAY;
            form.destroy();
        });

        QUnit.test('itemdroppedondiscardwithemptyrequiredfieldwith"Addanitem"(invalidon"ADD")',asyncfunction(assert){
            //whenarecordinalistisaddedwith"Addanitem",itshould
            //alwaysbedroppedondiscardifsomerequiredfieldareempty
            //attherecordcreation.
            assert.expect(6);

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<form>'+
                    '<fieldname="p">'+
                    '<treeeditable="bottom">'+
                    '<fieldname="display_name"/>'+
                    '<fieldname="trululu"required="1"/>'+
                    '</tree>'+
                    '</field>'+
                    '</form>',
            });

            //Clickon"Addanitem"
            awaittestUtils.dom.click(form.$('.o_field_x2many_list_row_adda'));
            varcharField=form.$('.o_field_widget.o_field_char[name="display_name"]');
            varrequiredField=form.$('.o_field_widget.o_required_modifier[name="trululu"]');
            charField.val("sometext");
            assert.strictEqual(charField.length,1,
                "shouldhaveacharfield'display_name'onthisrecord");
            assert.doesNotHaveClass(charField,'o_required_modifier',
                "thecharfieldshouldnotberequiredonthisrecord");
            assert.strictEqual(charField.val(),"sometext",
                "shouldhaveenteredtextinthecharfieldonthisrecord");
            assert.strictEqual(requiredField.length,1,
                "shouldhavearequiredfield'trululu'onthisrecord");
            assert.strictEqual(requiredField.val().trim(),"",
                "shouldhaveemptystringintherequiredfieldonthisrecord");

            //clickonemptyrequiredfieldineditablelistrecord
            awaittestUtils.dom.click(requiredField);
            //clickoffsothattherequiredfieldstillstayempty
            awaittestUtils.dom.click($('body'));

            //recordshouldbedropped
            assert.containsNone(form,'.o_data_row',
                "shouldhavedroppedrecordintheeditablelist");

            form.destroy();
        });

        QUnit.test('itemnotdroppedondiscardwithemptyrequiredfieldwith"Addanitem"(invalidon"UPDATE")',asyncfunction(assert){
            //whenarecordinalistisaddedwith"Addanitem",itshould
            //betemporarilyaddedtothelistwhenitisvalid(e.g.required
            //fieldsarenon-empty).Iftherecordisupdatedsothattherequired
            //fieldisempty,anditisdiscarded,thentherecordshouldnotbe
            //dropped.
            assert.expect(8);

            varM2O_DELAY=relationalFields.FieldMany2One.prototype.AUTOCOMPLETE_DELAY;
            relationalFields.FieldMany2One.prototype.AUTOCOMPLETE_DELAY=0;

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<form>'+
                    '<fieldname="p">'+
                    '<treeeditable="bottom">'+
                    '<fieldname="display_name"/>'+
                    '<fieldname="trululu"required="1"/>'+
                    '</tree>'+
                    '</field>'+
                    '</form>',
            });

            assert.containsNone(form,'.o_data_row',
                "shouldinitiallynothaveanyrecordinthelist");

            //Clickon"Addanitem"
            awaittestUtils.dom.click(form.$('.o_field_x2many_list_row_adda'));
            assert.containsOnce(form,'.o_data_row',
                "shouldhaveatemporaryrecordinthelist");

            var$inputEditMode=form.$('.o_field_widget.o_required_modifier[name="trululu"]input');
            assert.strictEqual($inputEditMode.length,1,
                "shouldhavearequiredfield'trululu'onthisrecord");
            assert.strictEqual($inputEditMode.val(),"",
                "shouldhaveemptystringintherequiredfieldonthisrecord");

            //addsomethingtorequiredfieldandleaveeditmodeoftherecord
            awaittestUtils.dom.click($inputEditMode);
            awaittestUtils.dom.click($('li.ui-menu-item').first());
            awaittestUtils.dom.click($('body'));

            var$inputReadonlyMode=form.$('.o_data_cell.o_required_modifier');
            assert.containsOnce(form,'.o_data_row',
                "shouldnothavedroppedvalidrecordwhenleavingeditmode");
            assert.strictEqual($inputReadonlyMode.text(),"firstrecord",
                "shouldhaveputsomecontentintherequiredfieldonthisrecord");

            //removetherequiredfieldandleaveeditmodeoftherecord
            awaittestUtils.dom.click($('.o_data_row'));
            assert.containsOnce(form,'.o_data_row',
                "shouldnothavedroppedrecordinthelistondiscard(invalidonUPDATE)");
            assert.strictEqual($inputReadonlyMode.text(),"firstrecord",
                "shouldkeeppreviousvalidrequiredfieldcontentonthisrecord");

            relationalFields.FieldMany2One.prototype.AUTOCOMPLETE_DELAY=M2O_DELAY;
            form.destroy();
        });

        QUnit.test('listinform:default_getwithx2manycreate',asyncfunction(assert){
            assert.expect(3);
            this.data.partner.fields.timmy.default=[
                [0,0,{display_name:'brandonisthenewtimmy',name:'brandon'}]
            ];
            vardisplayName='brandonisthenewtimmy';
            this.data.partner.onchanges.timmy=function(obj){
                obj.int_field=obj.timmy.length;
            };

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<form>'+
                    '<sheet>'+
                    '<fieldname="timmy">'+
                    '<treeeditable="bottom">'+
                    '<fieldname="display_name"/>'+
                    '</tree>'+
                    '</field>'+
                    '<fieldname="int_field"/>'+
                    '</sheet>'+
                    '</form>',
                mockRPC:function(route,args){
                    if(args.method==='create'){
                        assert.deepEqual(args.args[0],{
                            int_field:2,
                            timmy:[
                                [6,false,[]],
                                //LPETODO1taskid-2261084:removethisentirecommentincludingcodesnippet
                                //whenthechangeinbehaviorhasbeenthoroughlytested.
                                //Wecan'tdistinguishavaluecomingfromadefault_get
                                //fromonecomingfromtheonchange,andsowecaneitherstoreand
                                //senditallthetime,ornever.
                                //[0,args.args[0].timmy[1][1],{display_name:displayName,name:'brandon'}],
                                [0,args.args[0].timmy[1][1],{display_name:displayName}],
                            ],
                        },"shouldsendthecorrectvaluestocreate");
                    }
                    returnthis._super.apply(this,arguments);
                },
            });

            assert.strictEqual($('td.o_data_cell:first').text(),'brandonisthenewtimmy',
                "shouldhavecreatedthenewrecordinthem2mwiththecorrectname");
            assert.strictEqual($('input.o_field_integer').val(),'1',
                "shouldhavecalledandexecutedtheonchangeproperly");

            //editthesubrecordandsave
            displayName='newvalue';
            awaittestUtils.dom.click(form.$('.o_data_cell'));
            awaittestUtils.fields.editInput(form.$('.o_data_cellinput'),displayName);
            awaittestUtils.form.clickSave(form);

            form.destroy();
        });

        QUnit.test('listinform:default_getwithx2manycreateandonchange',asyncfunction(assert){
            assert.expect(1);

            this.data.partner.fields.turtles.default=[[6,0,[2,3]]];

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
                    '<fieldname="int_field"/>'+
                    '</sheet>'+
                    '</form>',
                mockRPC:function(route,args){
                    if(args.method==='create'){
                        assert.deepEqual(args.args[0].turtles,[
                            [4,2,false],
                            [4,3,false],
                        ],'shouldsendpropercommandstocreatemethod');
                    }
                    returnthis._super.apply(this,arguments);
                },
            });

            awaittestUtils.form.clickSave(form);

            form.destroy();
        });

        QUnit.test('listinform:callbuttoninsubview',asyncfunction(assert){
            assert.expect(11);

            this.data.partner.records[0].p=[2];
            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<form>'+
                    '<sheet>'+
                    '<fieldname="p">'+
                    '<treeeditable="bottom">'+
                    '<fieldname="product_id"/>'+
                    '</tree>'+
                    '</field>'+
                    '</sheet>'+
                    '</form>',
                res_id:1,
                mockRPC:function(route,args){
                    if(route==='/web/dataset/call_kw/product/get_formview_id'){
                        returnPromise.resolve(false);
                    }
                    returnthis._super.apply(this,arguments);
                },
                intercepts:{
                    execute_action:function(event){
                        assert.strictEqual(event.data.env.model,'product',
                            'shouldcallwithcorrectmodelinenv');
                        assert.strictEqual(event.data.env.currentID,37,
                            'shouldcallwithcorrectcurrentIDinenv');
                        assert.deepEqual(event.data.env.resIDs,[37],
                            'shouldcallwithcorrectresIDsinenv');
                        assert.step(event.data.action_data.name);
                    },
                },
                archs:{
                    'product,false,form':'<formstring="Partners">'+
                        '<header>'+
                        '<buttonname="action"type="action"string="Justdoit!"/>'+
                        '<buttonname="object"type="object"string="Justdon\'tdoit!"/>'+
                        '<fieldname="display_name"/>'+
                        '</header>'+
                        '</form>',
                },
            });

            awaittestUtils.form.clickEdit(form);
            awaittestUtils.dom.click(form.$('td.o_data_cell:first'));
            awaittestUtils.dom.click(form.$('.o_external_button'));
            awaittestUtils.dom.click($('button:contains("Justdoit!")'));
            assert.verifySteps(['action']);
            assert.ok($('button:contains("Justdon\'tdoit!")').get(0).disabled);

            awaittestUtils.dom.click($('.modal.btn-secondary:contains(Discard)'));
            awaittestUtils.dom.click(form.$('.o_external_button'));
            awaittestUtils.dom.click($('button:contains("Justdon\'tdoit!")'));
            assert.verifySteps(['object']);
            form.destroy();
        });

        QUnit.test('X2Manysequencelistinmodal',asyncfunction(assert){
            assert.expect(5);

            this.data.partner.fields.sequence={string:'Sequence',type:'integer'};
            this.data.partner.records[0].sequence=1;
            this.data.partner.records[1].sequence=2;
            this.data.partner.onchanges={
                sequence:function(obj){
                    if(obj.id===2){
                        obj.sequence=1;
                        assert.step('onchangesequence');
                    }
                },
            };

            this.data.product.fields.turtle_ids={string:'Turtles',type:'one2many',relation:'turtle'};
            this.data.product.records[0].turtle_ids=[1];

            this.data.turtle.fields.partner_types_ids={string:"Partner",type:"one2many",relation:'partner'};
            this.data.turtle.fields.type_id={string:"PartnerType",type:"many2one",relation:'partner_type'};

            this.data.partner_type.fields.partner_ids={string:"Partner",type:"one2many",relation:'partner'};
            this.data.partner_type.records[0].partner_ids=[1,2];

            varform=awaitcreateView({
                View:FormView,
                model:'product',
                data:this.data,
                arch:'<form>'+
                    '<fieldname="name"/>'+
                    '<fieldname="turtle_ids"widget="one2many">'+
                    '<treestring="Turtles"editable="bottom">'+
                    '<fieldname="type_id"/>'+
                    '</tree>'+
                    '</field>'+
                    '</form>',
                archs:{
                    'partner_type,false,form':'<form><fieldname="partner_ids"/></form>',
                    'partner,false,list':'<treestring="Vendors">'+
                        '<fieldname="display_name"/>'+
                        '<fieldname="sequence"widget="handle"/>'+
                        '</tree>',
                },
                res_id:37,
                mockRPC:function(route,args){
                    if(route==='/web/dataset/call_kw/product/read'){
                        returnPromise.resolve([{id:37,name:'xphone',display_name:'leonardo',turtle_ids:[1]}]);
                    }
                    if(route==='/web/dataset/call_kw/turtle/read'){
                        returnPromise.resolve([{id:1,type_id:[12,'gold']}]);
                    }
                    if(route==='/web/dataset/call_kw/partner_type/get_formview_id'){
                        returnPromise.resolve(false);
                    }
                    if(route==='/web/dataset/call_kw/partner_type/read'){
                        returnPromise.resolve([{id:12,partner_ids:[1,2],display_name:'gold'}]);
                    }
                    if(route==='/web/dataset/call_kw/partner_type/write'){
                        assert.step('partner_typewrite');
                    }
                    returnthis._super.apply(this,arguments);
                },
            });

            awaittestUtils.form.clickEdit(form);
            awaittestUtils.dom.click(form.$('.o_data_cell'));
            awaittestUtils.dom.click(form.$('.o_external_button'));

            var$modal=$('.modal');
            assert.equal($modal.length,1,
                'Thereshouldbe1modalopened');

            var$handles=$modal.find('.ui-sortable-handle');
            assert.equal($handles.length,2,
                'Thereshouldbe2sequencehandlers');

            awaittestUtils.dom.dragAndDrop($handles.eq(1),
                $modal.find('tbodytr').first(),{position:'top'});

            //Savingthemodalandthentheoriginalmodel
            awaittestUtils.dom.click($modal.find('.modal-footer.btn-primary'));
            awaittestUtils.form.clickSave(form);

            assert.verifySteps(['onchangesequence','partner_typewrite']);

            form.destroy();
        });

        QUnit.test('autocompletioninamany2one,informviewwithadomain',asyncfunction(assert){
            assert.expect(1);

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<form>'+
                    '<fieldname="product_id"/>'+
                    '</form>',
                res_id:1,
                viewOptions:{
                    domain:[['trululu','=',4]]
                },
                mockRPC:function(route,args){
                    if(args.method==='name_search'){
                        assert.deepEqual(args.kwargs.args,[],"shouldnothaveadomain");
                    }
                    returnthis._super(route,args);
                }
            });
            awaittestUtils.form.clickEdit(form);

            testUtils.dom.click(form.$('.o_field_widget[name=product_id]input'));
            form.destroy();
        });

        QUnit.test('autocompletioninamany2one,informviewwithadatefield',asyncfunction(assert){
            assert.expect(1);

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<form>'+
                    '<fieldname="bar"/>'+
                    '<fieldname="date"/>'+
                    '<fieldname="trululu"domain="[(\'bar\',\'=\',True)]"/>'+
                    '</form>',
                res_id:2,
                mockRPC:function(route,args){
                    if(args.method==='name_search'){
                        assert.deepEqual(args.kwargs.args,[["bar","=",true]],"shouldnothaveadomain");
                    }
                    returnthis._super(route,args);
                },
            });
            awaittestUtils.form.clickEdit(form);

            testUtils.dom.click(form.$('.o_field_widget[name=trululu]input'));
            form.destroy();
        });

        QUnit.test('creatingrecordwithmany2onewithoptionalways_reload',asyncfunction(assert){
            assert.expect(2);

            this.data.partner.fields.trululu.default=1;
            this.data.partner.onchanges={
                trululu:function(obj){
                    obj.trululu=2;//[2,"secondrecord"];
                },
            };

            varcount=0;

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<form>'+
                    '<fieldname="trululu"options="{\'always_reload\':True}"/>'+
                    '</form>',
                mockRPC:function(route,args){
                    count++;
                    if(args.method==='name_get'&&args.args[0]===2){
                        returnPromise.resolve([[2,"helloworld\nsomuchnoise"]]);
                    }
                    returnthis._super(route,args);
                },
            });

            assert.strictEqual(count,2,"shouldhavedone2rpcs(onchangeandname_get)");
            assert.strictEqual(form.$('.o_field_widget[name=trululu]input').val(),'helloworld',
                "shouldhavetakenthecorrectdisplayname");
            form.destroy();
        });

        QUnit.test('selectingamany2one,thendiscarding',asyncfunction(assert){
            assert.expect(3);

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<fieldname="product_id"/>'+
                    '</form>',
                res_id:1,
            });
            assert.strictEqual(form.$('a[name=product_id]').text(),'','thetagashouldbeempty');
            awaittestUtils.form.clickEdit(form);

            awaittestUtils.fields.many2one.clickOpenDropdown('product_id');
            awaittestUtils.fields.many2one.clickItem('product_id','xphone');
            assert.strictEqual(form.$('.o_field_widget[name=product_id]input').val(),"xphone","shouldhaveselectedxphone");

            awaittestUtils.form.clickDiscard(form);
            assert.strictEqual(form.$('a[name=product_id]').text(),'','thetagashouldbeempty');
            form.destroy();
        });

        QUnit.test('domainandcontextarecorrectlyusedwhendoinganame_searchinam2o',asyncfunction(assert){
            assert.expect(4);

            this.data.partner.records[0].timmy=[12];

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:
                    '<formstring="Partners">'+
                    '<fieldname="product_id"'+
                    'domain="[[\'foo\',\'=\',\'bar\'],[\'foo\',\'=\',foo]]"'+
                    'context="{\'hello\':\'world\',\'test\':foo}"/>'+
                    '<fieldname="foo"/>'+
                    '<fieldname="trululu"context="{\'timmy\':timmy}"domain="[[\'id\',\'in\',timmy]]"/>'+
                    '<fieldname="timmy"widget="many2many_tags"invisible="1"/>'+
                    '</form>',
                res_id:1,
                session:{user_context:{hey:"ho"}},
                mockRPC:function(route,args){
                    if(args.method==='name_search'&&args.model==='product'){
                        assert.deepEqual(
                            args.kwargs.args,
                            [['foo','=','bar'],['foo','=','yop']],
                            'thefieldattrdomainshouldhavebeenusedfortheRPC(andevaluated)');
                        assert.deepEqual(
                            args.kwargs.context,
                            {hey:"ho",hello:"world",test:"yop"},
                            'thefieldattrcontextshouldhavebeenusedforthe'+
                            'RPC(evaluatedandmergedwiththesessionone)');
                        returnPromise.resolve([]);
                    }
                    if(args.method==='name_search'&&args.model==='partner'){
                        assert.deepEqual(args.kwargs.args,[['id','in',[12]]],
                            'thefieldattrdomainshouldhavebeenusedfortheRPC(andevaluated)');
                        assert.deepEqual(args.kwargs.context,{hey:'ho',timmy:[[6,false,[12]]]},
                            'thefieldattrcontextshouldhavebeenusedfortheRPC(andevaluated)');
                        returnPromise.resolve([]);
                    }
                    returnthis._super.apply(this,arguments);
                },
            });

            awaittestUtils.form.clickEdit(form);
            testUtils.dom.click(form.$('.o_field_widget[name=product_id]input'));

            testUtils.dom.click(form.$('.o_field_widget[name=trululu]input'));

            form.destroy();
        });

        QUnit.test('quickcreateonamany2one',asyncfunction(assert){
            assert.expect(2);

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<sheet>'+
                    '<fieldname="product_id"/>'+
                    '</sheet>'+
                    '</form>',
                mockRPC:function(route,args){
                    if(route==='/web/dataset/call_kw/product/name_create'){
                        assert.strictEqual(args.args[0],'newpartner',
                            "shouldnamecreateanewproduct");
                    }
                    returnthis._super.apply(this,arguments);
                },
            });

            awaittestUtils.dom.triggerEvent(form.$('.o_field_many2oneinput'),'focus');
            awaittestUtils.fields.editAndTrigger(form.$('.o_field_many2oneinput'),
            'newpartner',['keyup','blur']);
            awaittestUtils.dom.click($('.modal.modal-footer.btn-primary').first());
            assert.strictEqual($('.modal.modal-body').text().trim(),"DoyouwanttocreatenewpartnerasanewProduct?");

            form.destroy();
        });

        QUnit.test('failingquickcreateonamany2one',asyncfunction(assert){
            assert.expect(4);

            constform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<form><fieldname="product_id"/></form>',
                archs:{
                    'product,false,form':'<form><fieldname="name"/></form>',
                },
                mockRPC(route,args){
                    if(args.method==='name_create'){
                        returnPromise.reject();
                    }
                    if(args.method==='create'){
                        assert.deepEqual(args.args[0],{name:'xyz'});
                    }
                    returnthis._super(...arguments);
                },
            });

            awaittestUtils.fields.many2one.searchAndClickItem('product_id',{
                search:'abcd',
                item:'Create"abcd"',
            });
            assert.containsOnce(document.body,'.modal.o_form_view');
            assert.strictEqual($('.o_field_widget[name=name]').val(),'abcd');

            awaittestUtils.fields.editInput($('.modal.o_field_widget[name=name]'),'xyz');
            awaittestUtils.dom.click($('.modal.modal-footer.btn-primary'));
            assert.strictEqual(form.$('.o_field_widget[name=product_id]input').val(),'xyz');

            form.destroy();
        });

        QUnit.test('failingquickcreateonamany2oneinsideaone2many',asyncfunction(assert){
            assert.expect(4);

            constform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<form><fieldname="p"/></form>',
                archs:{
                    'partner,false,list':'<treeeditable="bottom"><fieldname="product_id"/></tree>',
                    'product,false,form':'<form><fieldname="name"/></form>',
                },
                mockRPC(route,args){
                    if(args.method==='name_create'){
                        returnPromise.reject();
                    }
                    if(args.method==='create'){
                        assert.deepEqual(args.args[0],{name:'xyz'});
                    }
                    returnthis._super(...arguments);
                },
            });

            awaittestUtils.dom.click(form.$('.o_field_x2many_list_row_adda'));
            awaittestUtils.fields.many2one.searchAndClickItem('product_id',{
                search:'abcd',
                item:'Create"abcd"',
            });
            assert.containsOnce(document.body,'.modal.o_form_view');
            assert.strictEqual($('.o_field_widget[name=name]').val(),'abcd');

            awaittestUtils.fields.editInput($('.modal.o_field_widget[name=name]'),'xyz');
            awaittestUtils.dom.click($('.modal.modal-footer.btn-primary'));
            assert.strictEqual(form.$('.o_field_widget[name=product_id]input').val(),'xyz');

            form.destroy();
        });

        QUnit.test('slowcreateonamany2one',asyncfunction(assert){
            assert.expect(11);

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:
                    '<form>'+
                    '<sheet>'+
                    '<fieldname="product_id"options="{\'quick_create\':False}"/>'+
                    '</sheet>'+
                    '</form>',
                archs:{
                    'product,false,form':
                        '<form>'+
                        '<fieldname="name"/>'+
                        '</form>',
                },
            });

            //cancelthemany2onecreationwithCancelbutton
            form.$('.o_field_many2oneinput').focus().val('newproduct').trigger('keyup').trigger('blur');
            awaittestUtils.nextTick();
            assert.strictEqual($('.modal').length,1,"thereshouldbeoneopenedmodal");

            awaittestUtils.dom.click($('.modal.modal-footer.btn:contains(Cancel)'));
            assert.strictEqual($('.modal').length,0,"themodalshouldbeclosed");
            assert.strictEqual(form.$('.o_field_many2oneinput').val(),"",
                'themany2oneshouldnotsetavalueasitscreationhasbeencancelled(withCancelbutton)');

            //cancelthemany2onecreationwithClosebutton
            awaittestUtils.fields.editAndTrigger(form.$('.o_field_many2oneinput'),
                'newproduct',['keyup','blur']);
            assert.strictEqual($('.modal').length,1,"thereshouldbeoneopenedmodal");
            awaittestUtils.dom.click($('.modal.modal-headerbutton'));
            assert.strictEqual(form.$('.o_field_many2oneinput').val(),"",
                'themany2oneshouldnotsetavalueasitscreationhasbeencancelled(withClosebutton)');
            assert.strictEqual($('.modal').length,0,"themodalshouldbeclosed");

            //selectanewvaluethencancelthecreationofthenewone-->restoretheprevious
            awaittestUtils.fields.many2one.clickOpenDropdown('product_id');
            awaittestUtils.fields.many2one.clickItem('product_id','o');
            assert.strictEqual(form.$('.o_field_many2oneinput').val(),"xphone","shouldhaveselectedxphone");

            form.$('.o_field_many2oneinput').focus().val('newproduct').trigger('keyup').trigger('blur');
            awaittestUtils.nextTick();
            assert.strictEqual($('.modal').length,1,"thereshouldbeoneopenedmodal");

            awaittestUtils.dom.click($('.modal.modal-footer.btn:contains(Cancel)'));
            assert.strictEqual(form.$('.o_field_many2oneinput').val(),"xphone",
                'shouldhaverestoredthemany2onewithitspreviousselectedvalue(xphone)');

            //confirmthemany2onecreation
            form.$('.o_field_many2oneinput').focus().val('newpartner').trigger('keyup').trigger('blur');
            awaittestUtils.nextTick();
            assert.strictEqual($('.modal').length,1,"thereshouldbeoneopenedmodal");

            awaittestUtils.dom.click($('.modal.modal-footer.btn-primary:contains(Createandedit)'));
            awaittestUtils.nextTick();
            assert.strictEqual($('.modal.o_form_view').length,1,
                'anewmodalshouldbeopenedandcontainaformview');

            awaittestUtils.dom.click($('.modal.o_form_button_cancel'));

            form.destroy();
        });

        QUnit.test('no_createoptiononamany2one',asyncfunction(assert){
            assert.expect(1);

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<sheet>'+
                    '<fieldname="product_id"options="{\'no_create\':True}"/>'+
                    '</sheet>'+
                    '</form>',
            });

            awaittestUtils.fields.editAndTrigger(form.$('.o_field_many2oneinput'),
                'newpartner',['keyup','focusout']);
            awaittestUtils.nextTick();
            assert.strictEqual($('.modal').length,0,"shouldnotdisplaythecreatemodal");
            form.destroy();
        });

        QUnit.test('can_createandcan_writeoptiononamany2one',asyncfunction(assert){
            assert.expect(5);

            this.data.product.options={
                can_create:"false",
                can_write:"false",
            };

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<sheet>'+
                    '<fieldname="product_id"can_create="false"can_write="false"/>'+
                    '</sheet>'+
                    '</form>',
                archs:{
                    'product,false,form':'<formstring="Products"><fieldname="display_name"/></form>',
                },
                mockRPC:function(route){
                    if(route==='/web/dataset/call_kw/product/get_formview_id'){
                        returnPromise.resolve(false);
                    }
                    returnthis._super.apply(this,arguments);
                },
            });

            awaittestUtils.dom.click(form.$('.o_field_many2oneinput'));
            assert.strictEqual($('.ui-autocomplete.o_m2o_dropdown_option:contains(Create)').length,0,
                "thereshouldn'tbeanyoptiontosearchandcreate");

            awaittestUtils.dom.click($('.ui-autocompleteli:contains(xpad)').mouseenter());
            assert.strictEqual(form.$('.o_field_many2oneinput').val(),"xpad",
                "thecorrectrecordshouldbeselected");
            assert.containsOnce(form,'.o_field_many2one.o_external_button',
                "thereshouldbeanexternalbuttondisplayed");

            awaittestUtils.dom.click(form.$('.o_field_many2one.o_external_button'));
            assert.strictEqual($('.modal.o_form_view.o_form_readonly').length,1,
                "thereshouldbeareadonlyformviewopened");

            awaittestUtils.dom.click($('.modal.o_form_button_cancel'));

            awaittestUtils.fields.editAndTrigger(form.$('.o_field_many2oneinput'),
                'newproduct',['keyup','focusout']);
            assert.strictEqual($('.modal').length,0,"shouldnotdisplaythecreatemodal");
            form.destroy();
        });

        QUnit.test('pressingenterinam2oinaneditablelist',asyncfunction(assert){
            assert.expect(9);
            varM2O_DELAY=relationalFields.FieldMany2One.prototype.AUTOCOMPLETE_DELAY;
            relationalFields.FieldMany2One.prototype.AUTOCOMPLETE_DELAY=0;

            varlist=awaitcreateView({
                View:ListView,
                model:'partner',
                data:this.data,
                arch:'<treeeditable="bottom"><fieldname="product_id"/></tree>',
            });

            awaittestUtils.dom.click(list.$('td.o_data_cell:first'));
            assert.containsOnce(list,'.o_selected_row',
                "shouldhavearowineditmode");

            //wenowwrite'a'andpressentertocheckthattheselectionis
            //working,andpreventthenavigation
            awaittestUtils.fields.editInput(list.$('td.o_data_cellinput:first'),'a');
            var$input=list.$('td.o_data_cellinput:first');
            var$dropdown=$input.autocomplete('widget');
            assert.ok($dropdown.is(':visible'),"autocompletedropdownshouldbevisible");

            //wenowtriggerENTERtoselectfirstchoice
            awaittestUtils.fields.triggerKeydown($input,'enter');
            assert.strictEqual($input[0],document.activeElement,
                "inputshouldstillbefocused");

            //wenowtriggeragainENTERtomakesurewecanmovetonextline
            awaittestUtils.fields.triggerKeydown($input,'enter');

            assert.notOk(document.contains($input[0]),
                "inputshouldnolongerbeindom");
            assert.hasClass(list.$('tr.o_data_row:eq(1)'),'o_selected_row',
                "secondrowshouldnowbeselected");

            //wenowwriteagain'a'inthecelltoselectxpad.Wewillnow
            //testwiththetabkey
            awaittestUtils.fields.editInput(list.$('td.o_data_cellinput:first'),'a');
            var$input=list.$('td.o_data_cellinput:first');
            var$dropdown=$input.autocomplete('widget');
            assert.ok($dropdown.is(':visible'),"autocompletedropdownshouldbevisible");
            awaittestUtils.fields.triggerKeydown($input,'tab');
            assert.strictEqual($input[0],document.activeElement,
                "inputshouldstillbefocused");

            //wenowtriggeragainENTERtomakesurewecanmovetonextline
            awaittestUtils.fields.triggerKeydown($input,'tab');

            assert.notOk(document.contains($input[0]),
                "inputshouldnolongerbeindom");
            assert.hasClass(list.$('tr.o_data_row:eq(2)'),'o_selected_row',
                "thirdrowshouldnowbeselected");
            list.destroy();
            relationalFields.FieldMany2One.prototype.AUTOCOMPLETE_DELAY=M2O_DELAY;
        });

        QUnit.test('pressingENTERona\'no_quick_create\'many2oneshouldopenaM2ODialog',asyncfunction(assert){
            assert.expect(2);

            varM2O_DELAY=relationalFields.FieldMany2One.prototype.AUTOCOMPLETE_DELAY;
            relationalFields.FieldMany2One.prototype.AUTOCOMPLETE_DELAY=0;

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<form>'+
                    '<fieldname="trululu"options="{\'no_quick_create\':True}"/>'+
                    '<fieldname="foo"/>'+
                    '</form>',
                archs:{
                    'partner,false,form':'<formstring="Partners"><fieldname="display_name"/></form>',
                },
            });

            var$input=form.$('.o_field_many2oneinput');
            awaittestUtils.fields.editInput($input,"Somethingthatdoesnotexist");
            $('.ui-autocomplete.ui-menu-itema:contains(Createand)').trigger('mouseenter');
            awaittestUtils.nextTick();
            awaittestUtils.fields.triggerKey('down',$input,'enter')
            awaittestUtils.fields.triggerKey('press',$input,'enter')
            awaittestUtils.fields.triggerKey('up',$input,'enter')
            $input.blur();
            assert.strictEqual($('.modal').length,1,
                "shouldhaveonemodalinbody");
            //Checkthatdiscardingclears$input
            awaittestUtils.dom.click($('.modal.o_form_button_cancel'));
            assert.strictEqual($input.val(),'',
                "thefieldshouldbeempty");
            form.destroy();
            relationalFields.FieldMany2One.prototype.AUTOCOMPLETE_DELAY=M2O_DELAY;
        });

        QUnit.test('selectavaluebypressingTABonamany2onewithonchange',asyncfunction(assert){
            assert.expect(3);

            this.data.partner.onchanges.trululu=function(){};

            varM2O_DELAY=relationalFields.FieldMany2One.prototype.AUTOCOMPLETE_DELAY;
            relationalFields.FieldMany2One.prototype.AUTOCOMPLETE_DELAY=0;
            varprom=testUtils.makeTestPromise();

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<form>'+
                    '<fieldname="trululu"/>'+
                    '<fieldname="display_name"/>'+
                    '</form>',
                mockRPC:function(route,args){
                    varresult=this._super.apply(this,arguments);
                    if(args.method==='onchange'){
                        returnprom.then(_.constant(result));
                    }
                    returnresult;
                },
                res_id:1,
                viewOptions:{
                    mode:'edit',
                },
            });

            var$input=form.$('.o_field_many2oneinput');
            awaittestUtils.fields.editInput($input,"first");
            awaittestUtils.fields.triggerKey('down',$input,'tab');
            awaittestUtils.fields.triggerKey('press',$input,'tab');
            awaittestUtils.fields.triggerKey('up',$input,'tab');

            //simulateafocusout(e.g.becausetheuserclicksoutside)
            //beforetheonchangereturns
            form.$('.o_field_char').focus();

            assert.strictEqual($('.modal').length,0,
                "thereshouldn'tbeanymodalinbody");

            //unlocktheonchange
            prom.resolve();
            awaittestUtils.nextTick();

            assert.strictEqual($input.val(),'firstrecord',
                "firstrecordshouldhavebeenselected");
            assert.strictEqual($('.modal').length,0,
                "thereshouldn'tbeanymodalinbody");
            relationalFields.FieldMany2One.prototype.AUTOCOMPLETE_DELAY=M2O_DELAY;
            form.destroy();
        });

        QUnit.test('many2oneineditablelist+onchange,withenter[REQUIREFOCUS]',asyncfunction(assert){
            assert.expect(6);
            varM2O_DELAY=relationalFields.FieldMany2One.prototype.AUTOCOMPLETE_DELAY;
            relationalFields.FieldMany2One.prototype.AUTOCOMPLETE_DELAY=0;

            this.data.partner.onchanges.product_id=function(obj){
                obj.int_field=obj.product_id||0;
            };

            varprom=testUtils.makeTestPromise();

            varlist=awaitcreateView({
                View:ListView,
                model:'partner',
                data:this.data,
                arch:'<treeeditable="bottom"><fieldname="product_id"/><fieldname="int_field"/></tree>',
                mockRPC:function(route,args){
                    if(args.method){
                        assert.step(args.method);
                    }
                    varresult=this._super.apply(this,arguments);
                    if(args.method==='onchange'){
                        returnprom.then(_.constant(result));
                    }
                    returnresult;
                },
            });

            awaittestUtils.dom.click(list.$('td.o_data_cell:first'));
            awaittestUtils.fields.editInput(list.$('td.o_data_cellinput:first'),'a');
            var$input=list.$('td.o_data_cellinput:first');
            awaittestUtils.fields.triggerKeydown($input,'enter');
            awaittestUtils.fields.triggerKey('up',$input,'enter');
            prom.resolve();
            awaittestUtils.nextTick();
            awaittestUtils.fields.triggerKeydown($input,'enter');
            assert.strictEqual($('.modal').length,0,"shouldnothaveanymodalinDOM");
            assert.verifySteps(['name_search','onchange','write','read']);
            list.destroy();
            relationalFields.FieldMany2One.prototype.AUTOCOMPLETE_DELAY=M2O_DELAY;
        });

        QUnit.test('many2oneineditablelist+onchange,withenter,part2[REQUIREFOCUS]',asyncfunction(assert){
            //thisisthesametestasthepreviousone,buttheonchangeisjust
            //resolvedslightlylater
            assert.expect(6);
            varM2O_DELAY=relationalFields.FieldMany2One.prototype.AUTOCOMPLETE_DELAY;
            relationalFields.FieldMany2One.prototype.AUTOCOMPLETE_DELAY=0;

            this.data.partner.onchanges.product_id=function(obj){
                obj.int_field=obj.product_id||0;
            };

            varprom=testUtils.makeTestPromise();

            varlist=awaitcreateView({
                View:ListView,
                model:'partner',
                data:this.data,
                arch:'<treeeditable="bottom"><fieldname="product_id"/><fieldname="int_field"/></tree>',
                mockRPC:function(route,args){
                    if(args.method){
                        assert.step(args.method);
                    }
                    varresult=this._super.apply(this,arguments);
                    if(args.method==='onchange'){
                        returnprom.then(_.constant(result));
                    }
                    returnresult;
                },
            });

            awaittestUtils.dom.click(list.$('td.o_data_cell:first'));
            awaittestUtils.fields.editInput(list.$('td.o_data_cellinput:first'),'a');
            var$input=list.$('td.o_data_cellinput:first');
            awaittestUtils.fields.triggerKeydown($input,'enter');
            awaittestUtils.fields.triggerKey('up',$input,'enter');
            awaittestUtils.fields.triggerKeydown($input,'enter');
            prom.resolve();
            awaittestUtils.nextTick();
            assert.strictEqual($('.modal').length,0,"shouldnothaveanymodalinDOM");
            assert.verifySteps(['name_search','onchange','write','read']);
            list.destroy();
            relationalFields.FieldMany2One.prototype.AUTOCOMPLETE_DELAY=M2O_DELAY;
        });

        QUnit.test('many2one:domainupdatedbyanonchange',asyncfunction(assert){
            assert.expect(2);

            this.data.partner.onchanges={
                int_field:function(){},
            };

            vardomain=[];
            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<form>'+
                    '<fieldname="int_field"/>'+
                    '<fieldname="trululu"/>'+
                    '</form>',
                res_id:1,
                mockRPC:function(route,args){
                    if(args.method==='onchange'){
                        domain=[['id','in',[10]]];
                        returnPromise.resolve({
                            domain:{
                                trululu:domain,
                                unexisting_field:domain,
                            }
                        });
                    }
                    if(args.method==='name_search'){
                        assert.deepEqual(args.kwargs.args,domain,
                            "sentdomainshouldbecorrect");
                    }
                    returnthis._super(route,args);
                },
                viewOptions:{
                    mode:'edit',
                },
            });

            //triggeraname_search(domainshouldbe[])
            awaittestUtils.dom.click(form.$('.o_field_widget[name=trululu]input'));
            //closethedropdown
            awaittestUtils.dom.click(form.$('.o_field_widget[name=trululu]input'));
            //triggeranonchangethatwillupdatethedomain
            awaittestUtils.fields.editInput(form.$('.o_field_widget[name=int_field]'),2);
            //triggeraname_search(domainshouldbe[['id','in',[10]]])
            awaittestUtils.dom.click(form.$('.o_field_widget[name=trululu]input'));

            form.destroy();
        });

        QUnit.test('many2oneinone2many:domainupdatedbyanonchange',asyncfunction(assert){
            assert.expect(3);

            this.data.partner.onchanges={
                trululu:function(){},
            };

            vardomain=[];
            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<form>'+
                    '<fieldname="p">'+
                    '<treeeditable="bottom">'+
                    '<fieldname="trululu"/>'+
                    '</tree>'+
                    '</field>'+
                    '</form>',
                res_id:1,
                mockRPC:function(route,args){
                    if(args.method==='onchange'){
                        returnPromise.resolve({
                            domain:{
                                trululu:domain,
                            },
                        });
                    }
                    if(args.method==='name_search'){
                        assert.deepEqual(args.kwargs.args,domain,
                            "sentdomainshouldbecorrect");
                    }
                    returnthis._super(route,args);
                },
                viewOptions:{
                    mode:'edit',
                },
            });

            //addafirstrowwithaspecificdomainforthem2o
            domain=[['id','in',[10]]];//domainforsubrecord1
            awaittestUtils.dom.click(form.$('.o_field_x2many_list_row_adda'));
            awaittestUtils.dom.click(form.$('.o_field_widget[name=trululu]input'));

            //addasecondrowwithanotherdomainforthem2o
            domain=[['id','in',[5]]];//domainforsubrecord2
            awaittestUtils.dom.click(form.$('.o_field_x2many_list_row_adda'));
            awaittestUtils.dom.click(form.$('.o_field_widget[name=trululu]input'));

            //checkagainthefirstrowtoensurethatthedomainhasn'tchange
            domain=[['id','in',[10]]];//domainforsubrecord1shouldhavebeenkept
            awaittestUtils.dom.click(form.$('.o_data_row:first.o_data_cell'));
            awaittestUtils.dom.click(form.$('.o_field_widget[name=trululu]input'));

            form.destroy();
        });

        QUnit.test('searchmoreinmany2one:notextininput',asyncfunction(assert){
            //whentheuserclickson'SearchMore...'inamany2onedropdown,andthereisnotext
            //intheinput(i.e.novaluetosearchon),webypassthename_searchthatismeantto
            //returnalistofpreselectedidstofilteroninthelistview(openedinadialog)
            assert.expect(6);

            for(vari=0;i<8;i++){
                this.data.partner.records.push({id:100+i,display_name:'test_'+i});
            }

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<form><fieldname="trululu"/></form>',
                archs:{
                    'partner,false,list':'<list><fieldname="display_name"/></list>',
                    'partner,false,search':'<search></search>',
                },
                mockRPC:function(route,args){
                    assert.step(args.method||route);
                    if(route==='/web/dataset/search_read'){
                        assert.deepEqual(args.domain,[],
                            "shouldnotpreselectidsasthereasnothinginthem2oinput");
                    }
                    returnthis._super.apply(this,arguments);
                },
            });

            awaittestUtils.fields.many2one.searchAndClickItem('trululu',{
                item:'SearchMore',
                search:'',
            });

            assert.verifySteps([
                'onchange',
                'name_search',//todisplayresultsinthedropdown
                'load_views',//listviewindialog
                '/web/dataset/search_read',//todisplayresultsinthedialog
            ]);

            form.destroy();
        });

        QUnit.test('searchmoreinmany2one:textininput',asyncfunction(assert){
            //whentheuserclickson'SearchMore...'inamany2onedropdown,andthereissome
            //textintheinput,weperformaname_searchtogeta(limited)listofpreselected
            //idsandweaddadynamicfilter(withthoseids)tothesearchviewinthedialog,so
            //thattheusercanremovethisfiltertobypassthelimit
            assert.expect(12);

            for(vari=0;i<8;i++){
                this.data.partner.records.push({id:100+i,display_name:'test_'+i});
            }

            varexpectedDomain;
            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<form><fieldname="trululu"/></form>',
                archs:{
                    'partner,false,list':'<list><fieldname="display_name"/></list>',
                    'partner,false,search':'<search></search>',
                },
                mockRPC:function(route,args){
                    assert.step(args.method||route);
                    if(route==='/web/dataset/search_read'){
                        assert.deepEqual(args.domain,expectedDomain);
                    }
                    returnthis._super.apply(this,arguments);
                },
            });

            expectedDomain=[['id','in',[100,101,102,103,104,105,106,107]]];
            awaittestUtils.fields.many2one.searchAndClickItem('trululu',{
                item:'SearchMore',
                search:'test',
            });

            assert.containsOnce(document.body,'.modal.o_list_view');
            assert.containsOnce(document.body,'.modal.o_cp_searchview.o_facet_values',
                "shouldhaveaspecialfacetforthepre-selectedids");

            //removethefilteronids
            expectedDomain=[];
            awaittestUtils.dom.click($('.modal.o_cp_searchview.o_facet_remove'));

            assert.verifySteps([
                'onchange',
                'name_search',//emptysearch,triggeredwhentheuserclicksintheinput
                'name_search',//todisplayresultsinthedropdown
                'name_search',//togetpreselectedidsmatchingthesearch
                'load_views',//listviewindialog
                '/web/dataset/search_read',//todisplayresultsinthedialog
                '/web/dataset/search_read',//afterremovalofdynamicfilter
            ]);

            form.destroy();
        });

        QUnit.test('searchmoreinmany2one:dropdownclick',asyncfunction(assert){
            assert.expect(8);

            for(leti=0;i<8;i++){
                this.data.partner.records.push({id:100+i,display_name:'test_'+i});
            }

            //simulatemodal-likeelementrenderedbythefieldhtml
            const$fakeDialog=$(`<div>
                <divclass="pouet">
                    <divclass="modal"></div>
                </div>
            </div>`);
            $('body').append($fakeDialog);

            constform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<form><fieldname="trululu"/></form>',
                archs:{
                    'partner,false,list':'<list><fieldname="display_name"/></list>',
                    'partner,false,search':'<search></search>',
                },
            });
            awaittestUtils.fields.many2one.searchAndClickItem('trululu',{
                item:'SearchMore',
                search:'test',
            });

            //dropdownselector
            letfilterMenuCss='.o_search_options>.o_filter_menu';
            letgroupByMenuCss='.o_search_options>.o_group_by_menu';

            awaittestUtils.dom.click(document.querySelector(`${filterMenuCss}>.o_dropdown_toggler_btn`));

            assert.hasClass(document.querySelector(filterMenuCss),'show');
            assert.isVisible(document.querySelector(`${filterMenuCss}>.dropdown-menu`),
                "thefilterdropdownmenushouldbevisible");
            assert.doesNotHaveClass(document.querySelector(groupByMenuCss),'show');
            assert.isNotVisible(document.querySelector(`${groupByMenuCss}>.dropdown-menu`),
                "theGroupbydropdownmenushouldbenotvisible");

            awaittestUtils.dom.click(document.querySelector(`${groupByMenuCss}>.o_dropdown_toggler_btn`));
            assert.hasClass(document.querySelector(groupByMenuCss),'show');
            assert.isVisible(document.querySelector(`${groupByMenuCss}>.dropdown-menu`),
                "thegroupbydropdownmenushouldbevisible");
            assert.doesNotHaveClass(document.querySelector(filterMenuCss),'show');
            assert.isNotVisible(document.querySelector(`${filterMenuCss}>.dropdown-menu`),
                "thefilterdropdownmenushouldbenotvisible");

            $fakeDialog.remove();
            form.destroy();
        });

        QUnit.test('updatingamany2onefromamany2many',asyncfunction(assert){
            assert.expect(4);

            this.data.turtle.records[1].turtle_trululu=1;

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<group>'+
                    '<fieldname="turtles">'+
                    '<treeeditable="bottom">'+
                    '<fieldname="display_name"/>'+
                    '<fieldname="turtle_trululu"/>'+
                    '</tree>'+
                    '</field>'+
                    '</group>'+
                    '</form>',
                res_id:1,
                archs:{
                    'partner,false,form':'<formstring="Trululu"><fieldname="display_name"/></form>',
                },
                mockRPC:function(route,args){
                    if(args.method==='get_formview_id'){
                        assert.deepEqual(args.args[0],[1],"shouldcallget_formview_idwithcorrectid");
                        returnPromise.resolve(false);
                    }
                    returnthis._super(route,args);
                },
            });

            //Openingthemodal
            awaittestUtils.form.clickEdit(form);
            awaittestUtils.dom.click(form.$('.o_data_rowtd:contains(firstrecord)'));
            awaittestUtils.dom.click(form.$('.o_external_button'));
            assert.strictEqual($('.modal').length,1,
                "shouldhaveonemodalinbody");

            //Changingthe'trululu'value
            awaittestUtils.fields.editInput($('.modalinput[name="display_name"]'),'test');
            awaittestUtils.dom.click($('.modalbutton.btn-primary'));

            //Testwhetherthevaluehaschanged
            assert.strictEqual($('.modal').length,0,
                "themodalshouldbeclosed");
            assert.equal(form.$('.o_data_cell:contains(test)').text(),'test',
                "thepartnernameshouldhavebeenupdatedto'test'");

            form.destroy();
        });

        QUnit.test('searchmoreinmany2one:resequenceinsidedialog',asyncfunction(assert){
            //whentheuserclickson'SearchMore...'inamany2onedropdown,resequencinginside
            //thedialogworks
            assert.expect(10);

            this.data.partner.fields.sequence={string:'Sequence',type:'integer'};
            for(vari=0;i<8;i++){
                this.data.partner.records.push({id:100+i,display_name:'test_'+i});
            }

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<form><fieldname="trululu"/></form>',
                archs:{
                    'partner,false,list':'<list>'+
                        '<fieldname="sequence"widget="handle"/>'+
                        '<fieldname="display_name"/>'+
                    '</list>',
                    'partner,false,search':'<search></search>',
                },
                mockRPC:function(route,args){
                    assert.step(args.method||route);
                    if(route==='/web/dataset/search_read'){
                        assert.deepEqual(args.domain,[],
                            "shouldnotpreselectidsasthereasnothinginthem2oinput");
                    }
                    returnthis._super.apply(this,arguments);
                },
            });

            awaittestUtils.fields.many2one.searchAndClickItem('trululu',{
                item:'SearchMore',
                search:'',
            });

            var$modal=$('.modal');
            assert.equal($modal.length,1,
                'Thereshouldbe1modalopened');

            var$handles=$modal.find('.ui-sortable-handle');
            assert.equal($handles.length,11,
                'Thereshouldbe11sequencehandlers');

            awaittestUtils.dom.dragAndDrop($handles.eq(1),
                $modal.find('tbodytr').first(),{position:'top'});

            assert.verifySteps([
                'onchange',
                'name_search',//todisplayresultsinthedropdown
                'load_views',//listviewindialog
                '/web/dataset/search_read',//todisplayresultsinthedialog
                '/web/dataset/resequence',//resequencinglines
                'read',
            ]);

            form.destroy();
        });

        QUnit.test('many2onedropdowndisappearsonscroll',asyncfunction(assert){
            assert.expect(2);

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:
                    '<form>'+
                        '<divstyle="height:2000px;">'+
                            '<fieldname="trululu"/>'+
                        '</div>'+
                    '</form>',
                res_id:1,
            });

            awaittestUtils.form.clickEdit(form);

            var$input=form.$('.o_field_many2oneinput');

            awaittestUtils.dom.click($input);
            assert.isVisible($input.autocomplete('widget'),"dropdownshouldbeopened");

            form.el.dispatchEvent(newEvent('scroll'));
            assert.isNotVisible($input.autocomplete('widget'),"dropdownshouldbeclosed");

            form.destroy();
        });

        QUnit.test('x2manylistsortedbymany2one',asyncfunction(assert){
            assert.expect(3);

            this.data.partner.records[0].p=[1,2,4];
            this.data.partner.fields.trululu.sortable=true;

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<form>'+
                    '<fieldname="p">'+
                    '<tree>'+
                    '<fieldname="id"/>'+
                    '<fieldname="trululu"/>'+
                    '</tree>'+
                    '</field>'+
                    '</form>',
                res_id:1,
            });

            assert.strictEqual(form.$('.o_data_row.o_list_number').text(),'124',
                "shouldhavecorrectorderinitially");

            awaittestUtils.dom.click(form.$('.o_list_viewtheadth:nth(1)'));

            assert.strictEqual(form.$('.o_data_row.o_list_number').text(),'412',
                "shouldhavecorrectorder(ASC)");

            awaittestUtils.dom.click(form.$('.o_list_viewtheadth:nth(1)'));

            assert.strictEqual(form.$('.o_data_row.o_list_number').text(),'214',
                "shouldhavecorrectorder(DESC)");

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
                                        '</form>'},
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

        QUnit.test('one2manywithextrafieldfromservernotin(inline)form',asyncfunction(assert){
            assert.expect(1);

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
                            '<form>'+
                                '<fieldname="display_name"/>'+
                            '</form>'+
                        '</field>'+
                    '</form>',
                res_id:1,
                viewOptions:{
                    mode:'edit',
                },
            });

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

            form.destroy();
        });

        QUnit.test('one2manywithextraX2manyfieldfromservernotininlineform',asyncfunction(assert){
            assert.expect(1);

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                        '<fieldname="p">'+
                            '<tree>'+
                                '<fieldname="turtles"/>'+
                                '<fieldname="display_name"/>'+
                            '</tree>'+
                            '<form>'+
                                '<fieldname="display_name"/>'+
                            '</form>'+
                        '</field>'+
                    '</form>',
                res_id:1,
                viewOptions:{
                    mode:'edit',
                },
            });

            varx2mList=form.$('.o_field_x2many_list[name=p]');

            //Addafirstrecordinthelist
            awaittestUtils.dom.click(x2mList.find('.o_field_x2many_list_row_adda'));

            //Save&New
            awaittestUtils.dom.click($('.modal-lg').find('.btn-primary').eq(1));

            //Save&Close
            awaittestUtils.dom.click($('.modal-lg').find('.btn-primary').eq(0));

            assert.equal(x2mList.find('.o_data_row').length,2,
                'Thereshouldbe2recordsinthex2mlist');

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

        QUnit.module('Many2OneAvatar');

        QUnit.test('many2one_avatarwidgetinformview',asyncfunction(assert){
            assert.expect(10);

            constform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<form><fieldname="user_id"widget="many2one_avatar"/></form>',
                res_id:1,
            });

            assert.hasClass(form.$('.o_form_view'),'o_form_readonly');
            assert.strictEqual(form.$('.o_field_widget[name=user_id]').text().trim(),'Aline');
            assert.containsOnce(form,'img.o_m2o_avatar[data-src="/web/image/user/17/image_128"]');

            awaittestUtils.form.clickEdit(form);

            assert.hasClass(form.$('.o_form_view'),'o_form_editable');
            assert.containsOnce(form,'.o_input_dropdown');
            assert.strictEqual(form.$('.o_input_dropdowninput').val(),'Aline');
            assert.containsOnce(form,'.o_external_button');

            awaittestUtils.fields.many2one.clickOpenDropdown("user_id");
            awaittestUtils.fields.many2one.clickItem("user_id","Christine");
            awaittestUtils.form.clickSave(form);

            assert.hasClass(form.$('.o_form_view'),'o_form_readonly');
            assert.strictEqual(form.$('.o_field_widget[name=user_id]').text().trim(),'Christine');
            assert.containsOnce(form,'img.o_m2o_avatar[data-src="/web/image/user/19/image_128"]');

            form.destroy();
        });

        QUnit.test('many2one_avatarwidgetinformview,withonchange',asyncfunction(assert){
            assert.expect(7);

            this.data.partner.onchanges={
                int_field:function(obj){
                    if(obj.int_field===1){
                        obj.user_id=[19,'Christine'];
                    }elseif(obj.int_field===2){
                        obj.user_id=false;
                    }else{
                        obj.user_id=[17,'Aline'];//defaultvalue
                    }
                },
            };
            constform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:`
                    <form>
                        <fieldname="int_field"/>
                        <fieldname="user_id"widget="many2one_avatar"readonly="1"/>
                    </form>`,
            });

            assert.hasClass(form.$('.o_form_view'),'o_form_editable');
            assert.strictEqual(form.$('.o_field_widget[name=user_id]').text().trim(),'Aline');
            assert.containsOnce(form,'img.o_m2o_avatar[data-src="/web/image/user/17/image_128"]');

            awaittestUtils.fields.editInput(form.$('.o_field_widget[name=int_field]'),1);

            assert.strictEqual(form.$('.o_field_widget[name=user_id]').text().trim(),'Christine');
            assert.containsOnce(form,'img.o_m2o_avatar[data-src="/web/image/user/19/image_128"]');

            awaittestUtils.fields.editInput(form.$('.o_field_widget[name=int_field]'),2);

            assert.strictEqual(form.$('.o_field_widget[name=user_id]').text().trim(),'');
            assert.containsNone(form,'img.o_m2o_avatar');

            form.destroy();
        });

        QUnit.test('many2one_avatarwidgetinlistview',asyncfunction(assert){
            assert.expect(5);

            this.data.partner.records=[
                {id:1,user_id:17,},
                {id:2,user_id:19,},
                {id:3,user_id:17,},
                {id:4,user_id:false,},
            ];
            constlist=awaitcreateView({
                View:ListView,
                model:'partner',
                data:this.data,
                arch:'<tree><fieldname="user_id"widget="many2one_avatar"/></tree>',
            });

            assert.strictEqual(list.$('.o_data_cellspan').text(),'AlineChristineAline');
            assert.containsOnce(list.$('.o_data_cell:nth(0)'),'img.o_m2o_avatar[data-src="/web/image/user/17/image_128"]');
            assert.containsOnce(list.$('.o_data_cell:nth(1)'),'img.o_m2o_avatar[data-src="/web/image/user/19/image_128"]');
            assert.containsOnce(list.$('.o_data_cell:nth(2)'),'img.o_m2o_avatar[data-src="/web/image/user/17/image_128"]');
            assert.containsNone(list.$('.o_data_cell:nth(3)'),'img.o_m2o_avatar');

            list.destroy();
        });
    });
});
});
