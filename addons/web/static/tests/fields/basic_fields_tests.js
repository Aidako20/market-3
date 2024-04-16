flectra.define('web.basic_fields_tests',function(require){
"usestrict";

varajax=require('web.ajax');
varbasicFields=require('web.basic_fields');
varconcurrency=require('web.concurrency');
varconfig=require('web.config');
varcore=require('web.core');
varFormView=require('web.FormView');
varKanbanView=require('web.KanbanView');
varListView=require('web.ListView');
varsession=require('web.session');
vartestUtils=require('web.test_utils');
vartestUtilsDom=require('web.test_utils_dom');
varfield_registry=require('web.field_registry');

varcreateView=testUtils.createView;
varpatchDate=testUtils.mock.patchDate;

varDebouncedField=basicFields.DebouncedField;
varJournalDashboardGraph=basicFields.JournalDashboardGraph;
var_t=core._t;

//Base64imagesfortestingpurpose
constMY_IMAGE='iVBORw0KGgoAAAANSUhEUgAAAAUAAAAFCAYAAACNbyblAAAAHElEQVQI12P4//8/w38GIAXDIBKE0DHxgljNBAAO9TXL0Y4OHwAAAABJRU5ErkJggg==';
constPRODUCT_IMAGE='R0lGODlhDAAMAKIFAF5LAP/zxAAAANyuAP/gaP///wAAAAAAACH5BAEAAAUALAAAAAAMAAwAAAMlWLPcGjDKFYi9lxKBOaGcF35DhWHamZUW0K4mAbiwWtuf0uxFAgA7';
constFR_FLAG_URL='/base/static/img/country_flags/fr.png';
constEN_FLAG_URL='/base/static/img/country_flags/gb.png';


QUnit.module('fields',{},function(){

QUnit.module('basic_fields',{
    beforeEach:function(){
        this.data={
            partner:{
                fields:{
                    date:{string:"Adate",type:"date",searchable:true},
                    datetime:{string:"Adatetime",type:"datetime",searchable:true},
                    display_name:{string:"Displayedname",type:"char",searchable:true},
                    foo:{string:"Foo",type:"char",default:"MylittleFooValue",searchable:true,trim:true},
                    bar:{string:"Bar",type:"boolean",default:true,searchable:true},
                    empty_string:{string:"Emptystring",type:"char",default:false,searchable:true,trim:true},
                    txt:{string:"txt",type:"text",default:"MylittletxtValue\nHo-ho-hooooMerryChristmas"},
                    int_field:{string:"int_field",type:"integer",sortable:true,searchable:true},
                    qux:{string:"Qux",type:"float",digits:[16,1],searchable:true},
                    monetary:{string:"MMM",type:"monetary",digits:[16,1],searchable:true},
                    p:{string:"one2manyfield",type:"one2many",relation:'partner',searchable:true},
                    trululu:{string:"Trululu",type:"many2one",relation:'partner',searchable:true},
                    timmy:{string:"pokemon",type:"many2many",relation:'partner_type',searchable:true},
                    product_id:{string:"Product",type:"many2one",relation:'product',searchable:true},
                    sequence:{type:"integer",string:"Sequence",searchable:true},
                    currency_id:{string:"Currency",type:"many2one",relation:"currency",searchable:true},
                    selection:{string:"Selection",type:"selection",searchable:true,
                        selection:[['normal','Normal'],['blocked','Blocked'],['done','Done']]},
                    document:{string:"Binary",type:"binary"},
                    hex_color:{string:"hexadecimalcolor",type:"char"},
                },
                records:[{
                    id:1,
                    date:"2017-02-03",
                    datetime:"2017-02-0810:00:00",
                    display_name:"firstrecord",
                    bar:true,
                    foo:"yop",
                    int_field:10,
                    qux:0.44444,
                    p:[],
                    timmy:[],
                    trululu:4,
                    selection:'blocked',
                    document:'coucou==\n',
                    hex_color:'#ff0000',
                },{
                    id:2,
                    display_name:"secondrecord",
                    bar:true,
                    foo:"blip",
                    int_field:0,
                    qux:0,
                    p:[],
                    timmy:[],
                    trululu:1,
                    sequence:4,
                    currency_id:2,
                    selection:'normal',
                },{
                    id:4,
                    display_name:"aaa",
                    foo:"abc",
                    sequence:9,
                    int_field:false,
                    qux:false,
                    selection:'done',
                },
                {id:3,bar:true,foo:"gnap",int_field:80,qux:-3.89859},
                {id:5,bar:false,foo:"blop",int_field:-4,qux:9.1,currency_id:1,monetary:99.9}],
                onchanges:{},
            },
            team:{
                fields:{
                    partner_ids:{string:"Partner",type:"one2many",relation:'partner'},
                },
                records:[{
                    id:1,
                    partner_ids:[5],
                }],
                onchanges:{},
            },
            product:{
                fields:{
                    name:{string:"ProductName",type:"char",searchable:true}
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
                    name:{string:"PartnerType",type:"char",searchable:true},
                    color:{string:"Colorindex",type:"integer",searchable:true},
                },
                records:[
                    {id:12,display_name:"gold",color:2},
                    {id:14,display_name:"silver",color:5},
                ]
            },
            currency:{
                fields:{
                    digits:{string:"Digits"},
                    symbol:{string:"CurrencySumbol",type:"char",searchable:true},
                    position:{string:"CurrencyPosition",type:"char",searchable:true},
                },
                records:[{
                    id:1,
                    display_name:"$",
                    symbol:"$",
                    position:"before",
                },{
                    id:2,
                    display_name:"€",
                    symbol:"€",
                    position:"after",
                }]
            },
            "ir.translation":{
                fields:{
                    lang_code:{type:"char"},
                    value:{type:"char"},
                    res_id:{type:"integer"}
                },
                records:[{
                    id:99,
                    res_id:37,
                    value:'',
                    lang_code:'en_US'
                }]
            },
        };
    }
},function(){

    QUnit.module('DebouncedField');

    QUnit.test('debouncedfieldsdonottriggercall_setValueoncedestroyed',asyncfunction(assert){
        assert.expect(4);

        vardef=testUtils.makeTestPromise();
        var_doAction=DebouncedField.prototype._doAction;
        DebouncedField.prototype._doAction=function(){
            _doAction.apply(this,arguments);
            def.resolve();
        };
        var_setValue=DebouncedField.prototype._setValue;
        DebouncedField.prototype._setValue=function(){
            assert.step('_setValue');
            _setValue.apply(this,arguments);
        };

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
            fieldDebounce:3,
            viewOptions:{
                mode:'edit',
            },
        });

        //changethevalue
        testUtils.fields.editInput(form.$('input[name=foo]'),'newvalue');
        assert.verifySteps([],"_setValueshouldn'thavebeencalledyet");

        //save
        awaittestUtils.form.clickSave(form);
        assert.verifySteps(['_setValue'],"_setValueshouldhavebeencalledonce");

        //destroytheformview
        def=testUtils.makeTestPromise();
        form.destroy();
        awaittestUtils.nextMicrotaskTick();

        //waitforthedebouncedcallbacktobecalled
        assert.verifySteps([],
            "_setValueshouldnothavebeencalledafterwidgetdestruction");

        DebouncedField.prototype._doAction=_doAction;
        DebouncedField.prototype._setValue=_setValue;
    });

    QUnit.module('FieldBoolean');

    QUnit.test('booleanfieldinformview',asyncfunction(assert){
        assert.expect(13);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<form><labelfor="bar"string="Awesomecheckbox"/><fieldname="bar"/></form>',
            res_id:1,
        });

        assert.containsOnce(form,'.o_field_booleaninput:checked',
            "checkboxshouldbechecked");

        //switchtoeditmodeandchecktheresult
        awaittestUtils.form.clickEdit(form);
        assert.containsOnce(form,'.o_field_booleaninput:checked',
            "checkboxshouldstillbechecked");

        //uncheckthecheckbox
        awaittestUtils.dom.click(form.$('.o_field_booleaninput:checked'));
        assert.containsNone(form,'.o_field_booleaninput:checked',
            "checkboxshouldnolongerbechecked");

        //save
        awaittestUtils.form.clickSave(form);
        assert.containsNone(form,'.o_field_booleaninput:checked',
            "checkboxshouldstillnolongerbechecked");

        //switchtoeditmodeandtesttheoppositechange
        awaittestUtils.form.clickEdit(form);
        assert.containsNone(form,'.o_field_booleaninput:checked',
            "checkboxshouldstillbeunchecked");

        //checkthecheckbox
        awaittestUtils.dom.click(form.$('.o_field_booleaninput'));
        assert.containsOnce(form,'.o_field_booleaninput:checked',
            "checkboxshouldnowbechecked");

        //uncheckitback
        awaittestUtils.dom.click(form.$('.o_field_booleaninput'));
        assert.containsNone(form,'.o_field_booleaninput:checked',
            "checkboxshouldnowbeunchecked");

        //checkthecheckboxbyclickingonlabel
        awaittestUtils.dom.click(form.$('.o_form_viewlabel:first'));
        assert.containsOnce(form,'.o_field_booleaninput:checked',
            "checkboxshouldnowbechecked");

        //uncheckitback
        awaittestUtils.dom.click(form.$('.o_form_viewlabel:first'));
        assert.containsNone(form,'.o_field_booleaninput:checked',
            "checkboxshouldnowbeunchecked");

        //checkthecheckboxbyhittingthe"enter"keyafterfocusingit
        awaittestUtils.dom.triggerEvents(form.$('.o_field_booleaninput'),[
            "focusin",
            {type:"keydown",which:$.ui.keyCode.ENTER},
            {type:"keyup",which:$.ui.keyCode.ENTER}]);
        assert.containsOnce(form,'.o_field_booleaninput:checked',
        "checkboxshouldnowbechecked");
        //blindlypressenteragain,itshoulduncheckthecheckbox
        awaittestUtils.dom.triggerEvent(document.activeElement,"keydown",
            {which:$.ui.keyCode.ENTER});
        assert.containsNone(form,'.o_field_booleaninput:checked',
        "checkboxshouldnotbechecked");
        awaittestUtils.nextTick();
        //blindlypressenteragain,itshouldcheckthecheckboxback
        awaittestUtils.dom.triggerEvent(document.activeElement,"keydown",
            {which:$.ui.keyCode.ENTER});
        assert.containsOnce(form,'.o_field_booleaninput:checked',
            "checkboxshouldstillbechecked");

        //save
        awaittestUtils.form.clickSave(form);
        assert.containsOnce(form,'.o_field_booleaninput:checked',
            "checkboxshouldstillbechecked");
        form.destroy();
    });

    QUnit.test('booleanfieldineditablelistview',asyncfunction(assert){
        assert.expect(11);

        varlist=awaitcreateView({
            View:ListView,
            model:'partner',
            data:this.data,
            arch:'<treeeditable="bottom"><fieldname="bar"/></tree>',
        });

        assert.strictEqual(list.$('tbodytd:not(.o_list_record_selector).custom-checkboxinput').length,5,
            "shouldhave5checkboxes");
        assert.strictEqual(list.$('tbodytd:not(.o_list_record_selector).custom-checkboxinput:checked').length,4,
            "shouldhave4checkedinput");

        //Editaline
        var$cell=list.$('tr.o_data_row:has(.custom-checkboxinput:checked)td:not(.o_list_record_selector)').first();
        assert.ok($cell.find('.custom-checkboxinput:checked').prop('disabled'),
            "inputshouldbedisabledinreadonlymode");
        awaittestUtils.dom.click($cell);
        assert.ok(!$cell.find('.custom-checkboxinput:checked').prop('disabled'),
            "inputshouldnothavethedisabledpropertyineditmode");
        awaittestUtils.dom.click($cell.find('.custom-checkboxinput:checked'));

        //save
        awaittestUtils.dom.click(list.$buttons.find('.o_list_button_save'));
        $cell=list.$('tr.o_data_row:has(.custom-checkboxinput:not(:checked))td:not(.o_list_record_selector)').first();
        assert.ok($cell.find('.custom-checkboxinput:not(:checked)').prop('disabled'),
            "inputshouldbedisabledagain");
        assert.strictEqual(list.$('tbodytd:not(.o_list_record_selector).custom-checkboxinput').length,5,
            "shouldstillhave5checkboxes");
        assert.strictEqual(list.$('tbodytd:not(.o_list_record_selector).custom-checkboxinput:checked').length,3,
            "shouldnowhaveonly3checkedinput");

        //Re-Editthelineandfake-checkthecheckbox
        awaittestUtils.dom.click($cell);
        awaittestUtils.dom.click($cell.find('.custom-checkboxinput'));
        awaittestUtils.dom.click($cell.find('.custom-checkboxinput'));

        //Save
        awaittestUtils.dom.click(list.$buttons.find('.o_list_button_save'));
        assert.strictEqual(list.$('tbodytd:not(.o_list_record_selector).custom-checkboxinput').length,5,
            "shouldstillhave5checkboxes");
        assert.strictEqual(list.$('tbodytd:not(.o_list_record_selector).custom-checkboxinput:checked').length,3,
            "shouldstillhaveonly3checkedinput");

        //Re-Editthelinetocheckthecheckboxbackbutthistimeclickon
        //thecheckboxdirectlyinreadonlymode!
        $cell=list.$('tr.o_data_row:has(.custom-checkboxinput:not(:checked))td:not(.o_list_record_selector)').first();
        awaittestUtils.dom.click($cell.find('.custom-checkbox.custom-control-label'));
        awaittestUtils.nextTick();

        assert.strictEqual(list.$('tbodytd:not(.o_list_record_selector).custom-checkboxinput').length,5,
            "shouldstillhave5checkboxes");
        assert.strictEqual(list.$('tbodytd:not(.o_list_record_selector).custom-checkboxinput:checked').length,4,
            "shouldnowhave4checkedinputback");
        list.destroy();
    });

    QUnit.module('FieldBooleanToggle');

    QUnit.test('usebooleantogglewidgetinformview',asyncfunction(assert){
        assert.expect(1);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<form><fieldname="bar"widget="boolean_toggle"/></form>',
            res_id:2,
        });

        assert.containsOnce(form,".custom-checkbox.o_boolean_toggle","Booleantogglewidgetappliedtobooleanfield");
        form.destroy();
    });

    QUnit.test('booleantogglewidgetisnotdisabledinreadonlymode',asyncfunction(assert){
        assert.expect(3);

        constform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<form><fieldname="bar"widget="boolean_toggle"/></form>',
            res_id:5,
        });

        assert.containsOnce(form,".custom-checkbox.o_boolean_toggle","Booleantogglewidgetappliedtobooleanfield");
        assert.notOk(form.$('.o_boolean_toggleinput')[0].checked);
        awaittestUtils.dom.click(form.$('.o_boolean_toggle'));
        assert.ok(form.$('.o_boolean_toggleinput')[0].checked);
        form.destroy();
    });

    QUnit.test('booleantogglewidgetisdisabledwithareadonlyattribute',asyncfunction(assert){
        assert.expect(3);

        constform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<form><fieldname="bar"widget="boolean_toggle"readonly="1"/></form>',
            res_id:5,
        });

        assert.containsOnce(form,".custom-checkbox.o_boolean_toggle","Booleantogglewidgetappliedtobooleanfield");
        awaittestUtils.dom.click(form.$buttons.find('.o_form_button_edit'));
        assert.notOk(form.$('.o_boolean_toggleinput')[0].checked);
        awaittestUtils.dom.click(form.$('.o_boolean_toggle'));
        assert.notOk(form.$('.o_boolean_toggleinput')[0].checked);
        form.destroy();
    });

    QUnit.test('booleantogglewidgetisenabledineditmode',asyncfunction(assert){
        assert.expect(3);

        constform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<form><fieldname="bar"widget="boolean_toggle"/></form>',
            res_id:5,
        });

        assert.containsOnce(form,".custom-checkbox.o_boolean_toggle","Booleantogglewidgetappliedtobooleanfield");
        awaittestUtils.dom.click(form.$buttons.find('.o_form_button_edit'));

        assert.notOk(form.$('.o_boolean_toggleinput')[0].checked);
        awaittestUtils.dom.click(form.$('.o_boolean_toggle'));
        assert.ok(form.$('.o_boolean_toggleinput')[0].checked);
        form.destroy();
    });

    QUnit.module('FieldToggleButton');

    QUnit.test('usetoggle_buttoninlistview',asyncfunction(assert){
        assert.expect(6);

        varlist=awaitcreateView({
            View:ListView,
            model:'partner',
            data:this.data,
            arch:'<tree>'+
                    '<fieldname="bar"widget="toggle_button"'+
                        'options="{&quot;active&quot;:&quot;Reportedinlastpayslips&quot;,&quot;inactive&quot;:&quot;ToReportinPayslip&quot;}"/>'+
                '</tree>',
        });

        assert.containsN(list,'buttoni.fa.fa-circle.o_toggle_button_success',4,
            "shouldhave4greenbuttons");
        assert.containsOnce(list,'buttoni.fa.fa-circle.text-muted',
            "shouldhave1mutedbutton");

        assert.hasAttrValue(list.$('.o_list_viewbutton').first(),'title',
            "Reportedinlastpayslips","activebuttonsshouldhavepropertooltip");
        assert.hasAttrValue(list.$('.o_list_viewbutton').last(),'title',
            "ToReportinPayslip","inactivebuttonsshouldhavepropertooltip");

        //clickingonfirstbuttontocheckthestateisproperlychanged
        awaittestUtils.dom.click(list.$('.o_list_viewbutton').first());
        assert.containsN(list,'buttoni.fa.fa-circle.o_toggle_button_success',3,
            "shouldhave3greenbuttons");

        awaittestUtils.dom.click(list.$('.o_list_viewbutton').first());
        assert.containsN(list,'buttoni.fa.fa-circle.o_toggle_button_success',4,
            "shouldhave4greenbuttons");
        list.destroy();
    });

    QUnit.test('toggle_buttoninformview(editmode)',asyncfunction(assert){
        assert.expect(6);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<form>'+
                    '<fieldname="bar"widget="toggle_button"'+
                        'options="{\'active\':\'Activevalue\',\'inactive\':\'Inactivevalue\'}"/>'+
                '</form>',
            mockRPC:function(route,args){
                if(args.method==='write'){
                    assert.step('write');
                }
                returnthis._super.apply(this,arguments);
            },
            res_id:2,
            viewOptions:{
                mode:'edit',
            },
        });

        assert.strictEqual(form.$('.o_field_widget[name=bar]i.o_toggle_button_success:not(.text-muted)').length,
            1,"shouldbegreen");

        //clickonthebuttontotogglethevalue
        awaittestUtils.dom.click(form.$('.o_field_widget[name=bar]'));

        assert.strictEqual(form.$('.o_field_widget[name=bar]i.text-muted:not(.o_toggle_button_success)').length,
            1,"shouldbegray");
        assert.verifySteps([]);

        //save
        awaittestUtils.form.clickSave(form);

        assert.strictEqual(form.$('.o_field_widget[name=bar]i.text-muted:not(.o_toggle_button_success)').length,
            1,"shouldstillbegray");
        assert.verifySteps(['write']);

        form.destroy();
    });

    QUnit.test('toggle_buttoninformview(readonlymode)',asyncfunction(assert){
        assert.expect(4);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<form>'+
                    '<fieldname="bar"widget="toggle_button"'+
                        'options="{\'active\':\'Activevalue\',\'inactive\':\'Inactivevalue\'}"/>'+
                '</form>',
            mockRPC:function(route,args){
                if(args.method==='write'){
                    assert.step('write');
                }
                returnthis._super.apply(this,arguments);
            },
            res_id:2,
        });

        assert.strictEqual(form.$('.o_field_widget[name=bar]i.o_toggle_button_success:not(.text-muted)').length,
            1,"shouldbegreen");

        //clickonthebuttontotogglethevalue
        awaittestUtils.dom.click(form.$('.o_field_widget[name=bar]'));

        assert.strictEqual(form.$('.o_field_widget[name=bar]i.text-muted:not(.o_toggle_button_success)').length,
            1,"shouldbegray");
        assert.verifySteps(['write']);

        form.destroy();
    });

    QUnit.test('toggle_buttoninformviewwithreadonlymodifiers',asyncfunction(assert){
        assert.expect(3);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<form>'+
                '<fieldname="bar"widget="toggle_button"'+
                'options="{\'active\':\'Activevalue\',\'inactive\':\'Inactivevalue\'}"'+
                'readonly="True"/>'+
                '</form>',
            mockRPC:function(route,args){
                if(args.method==='write'){
                    thrownewError("ShouldnotdoawriteRPCwithreadonlytoggle_button");
                }
                returnthis._super.apply(this,arguments);
            },
            res_id:2,
        });

        assert.strictEqual(form.$('.o_field_widget[name=bar]i.o_toggle_button_success:not(.text-muted)').length,
            1,"shouldbegreen");
        assert.ok(form.$('.o_field_widget[name=bar]').prop('disabled'),
            "buttonshouldbedisabledwhenreadonlyattributeisgiven");

        //clickonthebuttontocheckclickdoesn'tcallwriteaswethrowerrorinwritecall
        form.$('.o_field_widget[name=bar]').click();

        assert.strictEqual(form.$('.o_field_widget[name=bar]i.o_toggle_button_success:not(.text-muted)').length,
            1,"shouldbegreenevenafterclick");

        form.destroy();
    });

    QUnit.module('FieldFloat');

    QUnit.test('floatfieldwhenunset',asyncfunction(assert){
        assert.expect(2);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<sheet>'+
                    '<fieldname="qux"digits="[5,3]"/>'+
                    '</sheet>'+
                '</form>',
            res_id:4,
        });

        assert.doesNotHaveClass(form.$('.o_field_widget'),'o_field_empty',
        'Non-setfloatfieldshouldbeconsideredas0.');
        assert.strictEqual(form.$('.o_field_widget').text(),"0.000",
        'Non-setfloatfieldshouldbeconsideredas0.');

        form.destroy();
    });

    QUnit.test('floatfieldsusecorrectdigitprecision',asyncfunction(assert){
        assert.expect(1);

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
            res_id:1,
        });
        assert.strictEqual(form.$('span.o_field_number:contains(0.4)').length,1,
                            "shouldcontainanumberroundedto1decimal");
        form.destroy();
    });

    QUnit.test('floatfieldinlistviewnowidget',asyncfunction(assert){
        assert.expect(5);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<sheet>'+
                        '<fieldname="qux"digits="[5,3]"/>'+
                    '</sheet>'+
                '</form>',
            res_id:2,
        });

        assert.doesNotHaveClass(form.$('.o_field_widget'),'o_field_empty',
            'Floatfieldshouldbeconsideredsetforvalue0.');
        assert.strictEqual(form.$('.o_field_widget').first().text(),'0.000',
            'Thevalueshouldbedisplayedproperly.');

        awaittestUtils.form.clickEdit(form);
        assert.strictEqual(form.$('input[name=qux]').val(),'0.000',
            'Thevalueshouldberenderedwithcorrectprecision.');

        awaittestUtils.fields.editInput(form.$('input[name=qux]'),'108.2458938598598');
        assert.strictEqual(form.$('input[name=qux]').val(),'108.2458938598598',
            'Thevalueshouldnotbeformatedyet.');

        awaittestUtils.fields.editInput(form.$('input[name=qux]'),'18.8958938598598');
        awaittestUtils.form.clickSave(form);
        assert.strictEqual(form.$('.o_field_widget').first().text(),'18.896',
            'Thenewvalueshouldberoundedproperly.');

        form.destroy();
    });

    QUnit.test('floatfieldinformview',asyncfunction(assert){
        assert.expect(5);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<sheet>'+
                        '<fieldname="qux"widget="float"digits="[5,3]"/>'+
                    '</sheet>'+
                '</form>',
            res_id:2,
        });

        assert.doesNotHaveClass(form.$('.o_field_widget'),'o_field_empty',
            'Floatfieldshouldbeconsideredsetforvalue0.');
        assert.strictEqual(form.$('.o_field_widget').first().text(),'0.000',
            'Thevalueshouldbedisplayedproperly.');

        awaittestUtils.form.clickEdit(form);
        assert.strictEqual(form.$('input[name=qux]').val(),'0.000',
            'Thevalueshouldberenderedwithcorrectprecision.');

        awaittestUtils.fields.editInput(form.$('input[name=qux]'),'108.2458938598598');
        assert.strictEqual(form.$('input[name=qux]').val(),'108.2458938598598',
            'Thevalueshouldnotbeformatedyet.');

        awaittestUtils.fields.editInput(form.$('input[name=qux]'),'18.8958938598598');
        awaittestUtils.form.clickSave(form);
        assert.strictEqual(form.$('.o_field_widget').first().text(),'18.896',
            'Thenewvalueshouldberoundedproperly.');

        form.destroy();
    });

    QUnit.test('floatfieldusingformulainformview',asyncfunction(assert){
        assert.expect(4);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<sheet>'+
                        '<fieldname="qux"widget="float"digits="[5,3]"/>'+
                    '</sheet>'+
                '</form>',
            res_id:2,
        });

        //Testcomputationwithpriorityofoperation
        awaittestUtils.form.clickEdit(form);
        awaittestUtils.fields.editInput(form.$('input[name=qux]'),'=20+3*2');
        awaittestUtils.form.clickSave(form);
        assert.strictEqual(form.$('.o_field_widget').first().text(),'26.000',
            'Thenewvalueshouldbecalculatedproperly.');

        //Testcomputationwith**operand
        awaittestUtils.form.clickEdit(form);
        awaittestUtils.fields.editInput(form.$('input[name=qux]'),'=2**3');
        awaittestUtils.form.clickSave(form);
        assert.strictEqual(form.$('.o_field_widget').first().text(),'8.000',
            'Thenewvalueshouldbecalculatedproperly.');

        //Testcomputationwith^operantwhichshoulddothesameas**
        awaittestUtils.form.clickEdit(form);
        awaittestUtils.fields.editInput(form.$('input[name=qux]'),'=2^3');
        awaittestUtils.form.clickSave(form);
        assert.strictEqual(form.$('.o_field_widget').first().text(),'8.000',
            'Thenewvalueshouldbecalculatedproperly.');

        //Testcomputationandrounding
        awaittestUtils.form.clickEdit(form);
        awaittestUtils.fields.editInput(form.$('input[name=qux]'),'=100/3');
        awaittestUtils.form.clickSave(form);
        assert.strictEqual(form.$('.o_field_widget').first().text(),'33.333',
            'Thenewvalueshouldbecalculatedproperly.');

        form.destroy();
    });

    QUnit.test('floatfieldusingincorrectformulainformview',asyncfunction(assert){
        assert.expect(4);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<sheet>'+
                        '<fieldname="qux"widget="float"digits="[5,3]"/>'+
                    '</sheet>'+
                '</form>',
            res_id:2,
        });

        //Testthatincorrectvalueisnotcomputed
        awaittestUtils.form.clickEdit(form);
        awaittestUtils.fields.editInput(form.$('input[name=qux]'),'=abc');
        awaittestUtils.form.clickSave(form);
        assert.hasClass(form.$('.o_form_view'),'o_form_editable',
            "formviewshouldstillbeeditable");
        assert.hasClass(form.$('input[name=qux]'),'o_field_invalid',
            "floadfieldshouldbedisplayedasinvalid");

        awaittestUtils.fields.editInput(form.$('input[name=qux]'),'=3:2?+4');
        awaittestUtils.form.clickSave(form);
        assert.hasClass(form.$('.o_form_view'),'o_form_editable',
            "formviewshouldstillbeeditable");
        assert.hasClass(form.$('input[name=qux]'),'o_field_invalid',
            "floatfieldshouldbedisplayedasinvalid");

        form.destroy();
    });

    QUnit.test('floatfieldineditablelistview',asyncfunction(assert){
        assert.expect(4);

        varlist=awaitcreateView({
            View:ListView,
            model:'partner',
            data:this.data,
            arch:'<treeeditable="bottom">'+
                    '<fieldname="qux"widget="float"digits="[5,3]"/>'+
                  '</tree>',
        });

        varzeroValues=list.$('td.o_data_cell').filter(function(){return$(this).text()==='';});
        assert.strictEqual(zeroValues.length,1,
            'Unsetfloatvaluesshouldberenderedasemptystrings.');

        //switchtoeditmode
        var$cell=list.$('tr.o_data_rowtd:not(.o_list_record_selector)').first();
        awaittestUtils.dom.click($cell);

        assert.containsOnce(list,'input[name="qux"]',
            'Theviewshouldhave1inputforeditablefloat.');

        awaittestUtils.fields.editInput(list.$('input[name="qux"]'),'108.2458938598598');
        assert.strictEqual(list.$('input[name="qux"]').val(),'108.2458938598598',
            'Thevalueshouldnotbeformatedyet.');

        awaittestUtils.fields.editInput(list.$('input[name="qux"]'),'18.8958938598598');
        awaittestUtils.dom.click(list.$buttons.find('.o_list_button_save'));
        assert.strictEqual(list.$('.o_field_widget').first().text(),'18.896',
            'Thenewvalueshouldberoundedproperly.');

        list.destroy();
    });

    QUnit.test('donottriggerafield_changediftheyhavenotchanged',asyncfunction(assert){
        assert.expect(2);

        this.data.partner.records[1].qux=false;
        this.data.partner.records[1].int_field=false;
        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<sheet>'+
                        '<fieldname="qux"widget="float"digits="[5,3]"/>'+
                        '<fieldname="int_field"/>'+
                    '</sheet>'+
                '</form>',
            res_id:2,
            mockRPC:function(route,args){
                assert.step(args.method);
                returnthis._super.apply(this,arguments);
            }
        });

        awaittestUtils.form.clickEdit(form);
        awaittestUtils.form.clickSave(form);

        assert.verifySteps(['read']);//shouldnothavesaveasnothingchanged

        form.destroy();
    });

    QUnit.test('floatwidgetonmonetaryfield',asyncfunction(assert){
        assert.expect(1);

        this.data.partner.fields.monetary={string:"Monetary",type:'monetary'};
        this.data.partner.records[0].monetary=9.99;
        this.data.partner.records[0].currency_id=1;

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<sheet>'+
                        '<fieldname="monetary"widget="float"/>'+
                        '<fieldname="currency_id"invisible="1"/>'+
                    '</sheet>'+
                '</form>',
            res_id:1,
            session:{
                currencies:_.indexBy(this.data.currency.records,'id'),
            },
        });

        assert.strictEqual(form.$('.o_field_widget[name=monetary]').text(),'9.99',
            'valueshouldbecorrectlyformatted(withthefloatformatter)');

        form.destroy();
    });

    QUnit.test('floatfieldwithmonetarywidgetanddecimalprecision',asyncfunction(assert){
        assert.expect(5);

        this.data.partner.records=[{
            id:1,
            qux:-8.89859,
            currency_id:1,
        }];
        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<sheet>'+
                        '<fieldname="qux"widget="monetary"options="{\'field_digits\':True}"/>'+
                        '<fieldname="currency_id"invisible="1"/>'+
                    '</sheet>'+
                '</form>',
            res_id:1,
            session:{
                currencies:_.indexBy(this.data.currency.records,'id'),
            },
        });

        //Non-breakingspacebetweenthecurrencyandtheamount
        assert.strictEqual(form.$('.o_field_widget').first().text(),'$\u00a0-8.9',
            'Thevalueshouldbedisplayedproperly.');

        awaittestUtils.form.clickEdit(form);
        assert.strictEqual(form.$('.o_field_widget[name=qux]input').val(),'-8.9',
            'Theinputshouldberenderedwithoutthecurrencysymbol.');
        assert.strictEqual(form.$('.o_field_widget[name=qux]input').parent().children().first().text(),'$',
            'Theinputshouldbeprecededbyaspancontainingthecurrencysymbol.');

        awaittestUtils.fields.editInput(form.$('.o_field_monetaryinput'),'109.2458938598598');
        assert.strictEqual(form.$('.o_field_widget[name=qux]input').val(),'109.2458938598598',
            'Thevalueshouldnotbeformatedyet.');

        awaittestUtils.form.clickSave(form);
        //Non-breakingspacebetweenthecurrencyandtheamount
        assert.strictEqual(form.$('.o_field_widget').first().text(),'$\u00a0109.2',
            'Thenewvalueshouldberoundedproperly.');

        form.destroy();
    });

    QUnit.test('floatfieldwithtypenumberoption',asyncfunction(assert){
        assert.expect(4);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                '<fieldname="qux"options="{\'type\':\'number\'}"/>'+
            '</form>',
            res_id:4,
            translateParameters:{
                thousands_sep:",",
                grouping:[3,0],
            },
        });

        awaittestUtils.form.clickEdit(form);
        assert.ok(form.$('.o_field_widget')[0].hasAttribute('type'),
            'Floatfieldwithoptiontypemusthaveatypeattribute.');
        assert.hasAttrValue(form.$('.o_field_widget'),'type','number',
            'Floatfieldwithoptiontypemusthaveatypeattributeequalsto"number".');
        awaittestUtils.fields.editInput(form.$('input[name=qux]'),'123456.7890');
        awaittestUtils.form.clickSave(form);
        awaittestUtils.form.clickEdit(form);
        assert.strictEqual(form.$('.o_field_widget').val(),'123456.789',
            'Floatvaluemustbenotformattedifinputtypeisnumber.');
        awaittestUtils.form.clickSave(form);
        assert.strictEqual(form.$('.o_field_widget').text(),'123,456.8',
            'Floatvaluemustbeformattedinreadonlyvieweveniftheinputtypeisnumber.');

        form.destroy();
    });

    QUnit.test('floatfieldwithtypenumberoptionandcommadecimalseparator',asyncfunction(assert){
        assert.expect(4);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                '<fieldname="qux"options="{\'type\':\'number\'}"/>'+
            '</form>',
            res_id:4,
            translateParameters:{
                thousands_sep:".",
                decimal_point:",",
                grouping:[3,0],
            },
        });

        awaittestUtils.form.clickEdit(form);
        assert.ok(form.$('.o_field_widget')[0].hasAttribute('type'),
            'Floatfieldwithoptiontypemusthaveatypeattribute.');
        assert.hasAttrValue(form.$('.o_field_widget'),'type','number',
            'Floatfieldwithoptiontypemusthaveatypeattributeequalsto"number".');
        awaittestUtils.fields.editInput(form.$('input[name=qux]'),'123456.789');
        awaittestUtils.form.clickSave(form);
        awaittestUtils.form.clickEdit(form);
        assert.strictEqual(form.$('.o_field_widget').val(),'123456.789',
            'Floatvaluemustbenotformattedifinputtypeisnumber.');
        awaittestUtils.form.clickSave(form);
        assert.strictEqual(form.$('.o_field_widget').text(),'123.456,8',
            'Floatvaluemustbeformattedinreadonlyvieweveniftheinputtypeisnumber.');

        form.destroy();
    });


    QUnit.test('floatfieldwithouttypenumberoption',asyncfunction(assert){
        assert.expect(2);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                '<fieldname="qux"/>'+
            '</form>',
            res_id:4,
            translateParameters:{
                thousands_sep:",",
                grouping:[3,0],
            },
        });

        awaittestUtils.form.clickEdit(form);
        assert.hasAttrValue(form.$('.o_field_widget'),'type','text',
            'Floatfieldwithoptiontypemusthaveatexttype(defaulttype).');

        awaittestUtils.fields.editInput(form.$('input[name=qux]'),'123456.7890');
        awaittestUtils.form.clickSave(form);
        awaittestUtils.form.clickEdit(form);
        assert.strictEqual(form.$('.o_field_widget').val(),'123,456.8',
            'Floatvaluemustbeformattedifinputtypeisn\'tnumber.');

        form.destroy();
    });

    QUnit.module('Percentage');

    QUnit.test('percentagewidgetinformview',asyncfunction(assert){
        assert.expect(6);

        constform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:`<formstring="Partners">
                        <fieldname="qux"widget="percentage"/>
                    </form>`,
            mockRPC:function(route,args){
                if(args.method==='write'){
                    assert.strictEqual(args.args[1].qux,0.24,'thecorrectfloatvalueshouldbesaved');
                }
                returnthis._super(...arguments);
            },
            res_id:1,
        });

        assert.strictEqual(form.$('.o_field_widget').first().text(),'44.4%',
            'Thevalueshouldbedisplayedproperly.');

        awaittestUtils.form.clickEdit(form);
        assert.strictEqual(form.$('.o_field_widget[name=qux]input').val(),'44.4',
            'Theinputshouldberenderedwithoutthepercentagesymbol.');
        assert.strictEqual(form.$('.o_field_widget[name=qux]span').text(),'%',
            'Theinputshouldbefollowedbyaspancontainingthepercentagesymbol.');

        awaittestUtils.fields.editInput(form.$('.o_field_float_percentageinput'),'24');
        assert.strictEqual(form.$('.o_field_widget[name=qux]input').val(),'24',
            'Thevalueshouldnotbeformatedyet.');

        awaittestUtils.form.clickSave(form);
        assert.strictEqual(form.$('.o_field_widget').text(),'24%',
            'Thenewvalueshouldbeformattedproperly.');

        form.destroy();
    });

    QUnit.module('FieldEmail');

    QUnit.test('emailfieldinformview',asyncfunction(assert){
        assert.expect(7);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<sheet>'+
                        '<group>'+
                            '<fieldname="foo"widget="email"/>'+
                        '</group>'+
                    '</sheet>'+
                '</form>',
            res_id:1,
        });

        var$mailtoLink=form.$('a.o_form_uri.o_field_widget.o_text_overflow');
        assert.strictEqual($mailtoLink.length,1,
            "shouldhaveaanchorwithcorrectclasses");
        assert.strictEqual($mailtoLink.text(),'yop',
            "thevalueshouldbedisplayedproperly");
        assert.hasAttrValue($mailtoLink,'href','mailto:yop',
            "shouldhavepropermailtoprefix");

        //switchtoeditmodeandchecktheresult
        awaittestUtils.form.clickEdit(form);
        assert.containsOnce(form,'input[type="text"].o_field_widget',
            "shouldhaveaninputfortheemailfield");
        assert.strictEqual(form.$('input[type="text"].o_field_widget').val(),'yop',
            "inputshouldcontainfieldvalueineditmode");

        //changevalueineditmode
        awaittestUtils.fields.editInput(form.$('input[type="text"].o_field_widget'),'new');

        //save
        awaittestUtils.form.clickSave(form);
        $mailtoLink=form.$('a.o_form_uri.o_field_widget.o_text_overflow');
        assert.strictEqual($mailtoLink.text(),'new',
            "newvalueshouldbedisplayedproperly");
        assert.hasAttrValue($mailtoLink,'href','mailto:new',
            "shouldstillhavepropermailtoprefix");

        form.destroy();
    });

    QUnit.test('emailfieldineditablelistview',asyncfunction(assert){
        assert.expect(10);

        varlist=awaitcreateView({
            View:ListView,
            model:'partner',
            data:this.data,
            arch:'<treeeditable="bottom"><fieldname="foo" widget="email"/></tree>',
        });

        assert.strictEqual(list.$('tbodytd:not(.o_list_record_selector)').length,5,
            "shouldhave5cells");
        assert.strictEqual(list.$('tbodytd:not(.o_list_record_selector)').first().text(),'yop',
            "valueshouldbedisplayedproperlyastext");

        var$mailtoLink=list.$('a.o_form_uri.o_field_widget.o_text_overflow');
        assert.strictEqual($mailtoLink.length,5,
            "shouldhaveanchorswithcorrectclasses");
        assert.hasAttrValue($mailtoLink.first(),'href','mailto:yop',
            "shouldhavepropermailtoprefix");

        //Editalineandchecktheresult
        var$cell=list.$('tbodytd:not(.o_list_record_selector)').first();
        awaittestUtils.dom.click($cell);
        assert.hasClass($cell.parent(),'o_selected_row','shouldbesetaseditmode');
        assert.strictEqual($cell.find('input').val(),'yop',
            'shouldhavethecorectvalueininternalinput');
        awaittestUtils.fields.editInput($cell.find('input'),'new');

        //save
        awaittestUtils.dom.click(list.$buttons.find('.o_list_button_save'));
        $cell=list.$('tbodytd:not(.o_list_record_selector)').first();
        assert.doesNotHaveClass($cell.parent(),'o_selected_row','shouldnotbeineditmodeanymore');
        assert.strictEqual(list.$('tbodytd:not(.o_list_record_selector)').first().text(),'new',
            "valueshouldbeproperlyupdated");
        $mailtoLink=list.$('a.o_form_uri.o_field_widget.o_text_overflow');
        assert.strictEqual($mailtoLink.length,5,
            "shouldstillhaveanchorswithcorrectclasses");
        assert.hasAttrValue($mailtoLink.first(),'href','mailto:new',
            "shouldstillhavepropermailtoprefix");

        list.destroy();
    });

    QUnit.test('emailfieldwithemptyvalue',asyncfunction(assert){
        assert.expect(1);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<sheet>'+
                        '<group>'+
                            '<fieldname="empty_string"widget="email"/>'+
                        '</group>'+
                    '</sheet>'+
                '</form>',
            res_id:1,
        });

        var$mailtoLink=form.$('a.o_form_uri.o_field_widget.o_text_overflow');
        assert.strictEqual($mailtoLink.text(),'',
            "thevalueshouldbedisplayedproperly");

        form.destroy();
    });

    QUnit.test('emailfieldtrimuservalue',asyncfunction(assert){
        assert.expect(1);

        constform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<form><fieldname="foo"widget="email"/></form>',
            res_id:1,
            viewOptions:{
                mode:'edit',
            },
        });

        awaittestUtils.fields.editInput(form.$('input[name="foo"]'),' abc@abc.com ');
        awaittestUtils.form.clickSave(form);
        awaittestUtils.form.clickEdit(form);
        assert.strictEqual(form.$('input[name="foo"]').val(),'abc@abc.com',
            "Foovalueshouldhavebeentrimmed");

        form.destroy();
    });


    QUnit.module('FieldChar');

    QUnit.test('charwidgetisValidmethodworks',asyncfunction(assert){
        assert.expect(1);

        this.data.partner.fields.foo.required=true;
        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                        '<fieldname="foo"/>'+
                '</form>',
            res_id:1,
        });

        varcharField=_.find(form.renderer.allFieldWidgets)[0];
        assert.strictEqual(charField.isValid(),true);
        form.destroy();
    });

    QUnit.test('charfieldinformview',asyncfunction(assert){
        assert.expect(4);

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

        assert.strictEqual(form.$('.o_field_widget').text(),'yop',
            "thevalueshouldbedisplayedproperly");

        //switchtoeditmodeandchecktheresult
        awaittestUtils.form.clickEdit(form);
        assert.containsOnce(form,'input[type="text"].o_field_widget',
            "shouldhaveaninputforthecharfield");
        assert.strictEqual(form.$('input[type="text"].o_field_widget').val(),'yop',
            "inputshouldcontainfieldvalueineditmode");

        //changevalueineditmode
        awaittestUtils.fields.editInput(form.$('input[type="text"].o_field_widget'),'limbo');

        //save
        awaittestUtils.form.clickSave(form);
        assert.strictEqual(form.$('.o_field_widget').text(),'limbo',
            'thenewvalueshouldbedisplayed');
        form.destroy();
    });

    QUnit.test('settingacharfieldtoemptystringissavedasafalsevalue',asyncfunction(assert){
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
            viewOptions:{mode:'edit'},
            mockRPC:function(route,args){
                if(args.method==='write'){
                    assert.strictEqual(args.args[1].foo,false,
                        'thefoovalueshouldbefalse');
                }
                returnthis._super.apply(this,arguments);
            }
        });

        awaittestUtils.fields.editInput(form.$('input[type="text"].o_field_widget'),'');

        //save
        awaittestUtils.form.clickSave(form);
        form.destroy();
    });

    QUnit.test('charfieldwithsizeattribute',asyncfunction(assert){
        assert.expect(1);

        this.data.partner.fields.foo.size=5;//maxlength
        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<form>'+
                    '<sheet>'+
                        '<group><fieldname="foo"/></group>'+
                    '</sheet>'+
                '</form>',
            res_id:1,
            viewOptions:{
                mode:'edit',
            },
        });

        assert.hasAttrValue(form.$('input.o_field_widget'),'maxlength','5',
            "maxlengthattributeshouldhavebeensetcorrectlyontheinput");

        form.destroy();
    });

    QUnit.test('charfieldineditablelistview',asyncfunction(assert){
        assert.expect(6);

        varlist=awaitcreateView({
            View:ListView,
            model:'partner',
            data:this.data,
            arch:'<treeeditable="bottom"><fieldname="foo"/></tree>',
        });

        assert.strictEqual(list.$('tbodytd:not(.o_list_record_selector)').length,5,
            "shouldhave5cells");
        assert.strictEqual(list.$('tbodytd:not(.o_list_record_selector)').first().text(),'yop',
            "valueshouldbedisplayedproperlyastext");

        //Editalineandchecktheresult
        var$cell=list.$('tbodytd:not(.o_list_record_selector)').first();
        awaittestUtils.dom.click($cell);
        assert.hasClass($cell.parent(),'o_selected_row','shouldbesetaseditmode');
        assert.strictEqual($cell.find('input').val(),'yop',
            'shouldhavethecorectvalueininternalinput');
        awaittestUtils.fields.editInput($cell.find('input'),'brolo');

        //save
        awaittestUtils.dom.click(list.$buttons.find('.o_list_button_save'));
        $cell=list.$('tbodytd:not(.o_list_record_selector)').first();
        assert.doesNotHaveClass($cell.parent(),'o_selected_row','shouldnotbeineditmodeanymore');
        assert.strictEqual(list.$('tbodytd:not(.o_list_record_selector)').first().text(),'brolo',
            "valueshouldbeproperlyupdated");
        list.destroy();
    });

    QUnit.test('charfieldtranslatable',asyncfunction(assert){
        assert.expect(12);

        this.data.partner.fields.foo.translate=true;

        varmultiLang=_t.database.multi_lang;
        _t.database.multi_lang=true;

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
            session:{
                user_context:{lang:'en_US'},
            },
            mockRPC:function(route,args){
                if(route==="/web/dataset/call_button"&&args.method==='translate_fields'){
                    assert.deepEqual(args.args,["partner",1,"foo"],'shouldcall"call_button"route');
                    returnPromise.resolve({
                        domain:[],
                        context:{search_default_name:'partnes,foo'},
                    });
                }
                if(route==="/web/dataset/call_kw/res.lang/get_installed"){
                    returnPromise.resolve([["en_US","English"],["fr_BE","French(Belgium)"]]);
                }
                if(args.method==="search_read"&&args.model=="ir.translation"){
                    returnPromise.resolve([
                        {lang:'en_US',src:'yop',value:'yop',id:42},
                        {lang:'fr_BE',src:'yop',value:'valeurfrançais',id:43}
                    ]);
                }
                if(args.method==="write"&&args.model=="ir.translation"){
                    assert.deepEqual(args.args[1],{value:"englishvalue"},
                        "thenewtranslationvalueshouldbewritten");
                    returnPromise.resolve();
                }
                returnthis._super.apply(this,arguments);
            },
        });
        awaittestUtils.form.clickEdit(form);
        var$button=form.$('input[type="text"].o_field_char+.o_field_translate');
        assert.strictEqual($button.length,1,"shouldhaveatranslatebutton");
        assert.strictEqual($button.text(),'EN','thebuttonshouldhaveastestthecurrentlanguage');
        awaittestUtils.dom.click($button);
        awaittestUtils.nextTick();

        assert.containsOnce($(document),'.modal','atranslatemodalshouldbevisible');
        assert.containsN($('.modal.o_translation_dialog'),'.translation',2,
            'tworowsshouldbevisible');

        var$enField=$('.modal.o_translation_dialog.translation:first()input');
        assert.strictEqual($enField.val(),'yop',
            'Englishtranslationshouldbefilled');
        assert.strictEqual($('.modal.o_translation_dialog.translation:last()input').val(),'valeurfrançais',
            'Frenchtranslationshouldbefilled');

        awaittestUtils.fields.editInput($enField,"englishvalue");
        awaittestUtils.dom.click($('.modalbutton.btn-primary')); //save
        awaittestUtils.nextTick();

        var$foo=form.$('input[type="text"].o_field_char');
        assert.strictEqual($foo.val(),"englishvalue",
            "thenewtranslationwasnottransferedtomodifiedrecord");

        awaittestUtils.fields.editInput($foo,"newenglishvalue");

        awaittestUtils.dom.click($button);
        awaittestUtils.nextTick();

        assert.strictEqual($('.modal.o_translation_dialog.translation:first()input').val(),'newenglishvalue',
            'Modifiedvalueshouldbeusedinsteadoftranslation');
        assert.strictEqual($('.modal.o_translation_dialog.translation:last()input').val(),'valeurfrançais',
            'Frenchtranslationshouldbefilled');

        form.destroy();

        _t.database.multi_lang=multiLang;
    });

    QUnit.test('htmlfieldtranslatable',asyncfunction(assert){
        assert.expect(6);

        this.data.partner.fields.foo.translate=true;

        varmultiLang=_t.database.multi_lang;
        _t.database.multi_lang=true;

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
            session:{
                user_context:{lang:'en_US'},
            },
            mockRPC:function(route,args){
                if(route==="/web/dataset/call_button"&&args.method==='translate_fields'){
                    assert.deepEqual(args.args,["partner",1,"foo"],'shouldcall"call_button"route');
                    returnPromise.resolve({
                        domain:[],
                        context:{
                            search_default_name:'partner,foo',
                            translation_type:'char',
                            translation_show_src:true,
                        },
                    });
                }
                if(route==="/web/dataset/call_kw/res.lang/get_installed"){
                    returnPromise.resolve([["en_US","English"],["fr_BE","French(Belgium)"]]);
                }
                if(args.method==="search_read"&&args.model=="ir.translation"){
                    returnPromise.resolve([
                        {lang:'en_US',src:'firstparagraph',value:'firstparagraph',id:42},
                        {lang:'en_US',src:'secondparagraph',value:'secondparagraph',id:43},
                        {lang:'fr_BE',src:'firstparagraph',value:'premierparagraphe',id:44},
                        {lang:'fr_BE',src:'secondparagraph',value:'deuxièmeparagraphe',id:45},
                    ]);
                }
                if(args.method==="write"&&args.model=="ir.translation"){
                    assert.deepEqual(args.args[1],{value:"firstparagraphmodified"},
                        "Wrongupdateontranslation");
                    returnPromise.resolve();
                }
                returnthis._super.apply(this,arguments);
            },
        });
        awaittestUtils.form.clickEdit(form);
        var$foo=form.$('input[type="text"].o_field_char');

        //thiswillnotaffectthetranslate_fieldseffectuntiltherecordis
        //savedbutissetforconsistencyofthetest
        awaittestUtils.fields.editInput($foo,"<p>firstparagraph</p><p>secondparagraph</p>");

        var$button=form.$('input[type="text"].o_field_char+.o_field_translate');
        awaittestUtils.dom.click($button);
        awaittestUtils.nextTick();

        assert.containsOnce($(document),'.modal','atranslatemodalshouldbevisible');
        assert.containsN($('.modal.o_translation_dialog'),'.translation',4,
            'fourrowsshouldbevisible');

        var$enField=$('.modal.o_translation_dialog.translation:first()input');
        assert.strictEqual($enField.val(),'firstparagraph',
            'firstpartofenglishtranslationshouldbefilled');

        awaittestUtils.fields.editInput($enField,"firstparagraphmodified");
        awaittestUtils.dom.click($('.modalbutton.btn-primary')); //save
        awaittestUtils.nextTick();

        assert.strictEqual($foo.val(),"<p>firstparagraph</p><p>secondparagraph</p>",
            "thenewpartialtranslationshouldnotbetransfered");

        form.destroy();

        _t.database.multi_lang=multiLang;
    });

    QUnit.test('charfieldtranslatableincreatemode',asyncfunction(assert){
        assert.expect(1);

        this.data.partner.fields.foo.translate=true;

        varmultiLang=_t.database.multi_lang;
        _t.database.multi_lang=true;


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
        });
        var$button=form.$('input[type="text"].o_field_char+.o_field_translate');
        assert.strictEqual($button.length,1,"shouldhaveatranslatebuttonincreatemode");
        form.destroy();

        _t.database.multi_lang=multiLang;
    });

    QUnit.test('charfielddoesnotallowhtmlinjections',asyncfunction(assert){
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
            viewOptions:{
                mode:'edit',
            },
        });

        awaittestUtils.fields.editInput(form.$('input[name=foo]'),'<script>throwError();</script>');
        awaittestUtils.form.clickSave(form);
        assert.strictEqual(form.$('.o_field_widget').text(),'<script>throwError();</script>',
            'thevalueshouldhavebeenproperlyescaped');

        form.destroy();
    });

    QUnit.test('charfieldtrim(ornot)characters',asyncfunction(assert){
        assert.expect(2);

        this.data.partner.fields.foo2={string:"Foo2",type:"char",trim:false};

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<sheet>'+
                        '<group>'+
                            '<fieldname="foo"/>'+
                            '<fieldname="foo2"/>'+
                        '</group>'+
                    '</sheet>'+
                '</form>',
            res_id:1,
            viewOptions:{
                mode:'edit',
            },
        });

        awaittestUtils.fields.editInput(form.$('input[name="foo"]'),' abc ');
        awaittestUtils.fields.editInput(form.$('input[name="foo2"]'),' def ');

        awaittestUtils.form.clickSave(form);

        //editmode
        awaittestUtils.form.clickEdit(form);

        assert.strictEqual(form.$('input[name="foo"]').val(),'abc','Foovalueshouldhavebeentrimmed');
        assert.strictEqual(form.$('input[name="foo2"]').val(),' def ','Foo2valueshouldnothavebeentrimmed');

        form.destroy();
    });

    QUnit.test('inputfield:changevaluebeforependingonchangereturns',asyncfunction(assert){
        assert.expect(3);

        this.data.partner.onchanges={
            product_id:function(){},
        };

        vardef;
        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<form>'+
                    '<sheet>'+
                        '<fieldname="p">'+
                            '<treeeditable="bottom">'+
                                '<fieldname="product_id"/>'+
                                '<fieldname="foo"/>'+
                            '</tree>'+
                        '</field>'+
                    '</sheet>'+
                '</form>',
            res_id:1,
            mockRPC:function(route,args){
                varresult=this._super.apply(this,arguments);
                if(args.method==="onchange"){
                    returnPromise.resolve(def).then(function(){
                        returnresult;
                    });
                }else{
                    returnresult;
                }
            },
            viewOptions:{
                mode:'edit',
            },
        });

        awaittestUtils.dom.click(form.$('.o_field_x2many_list_row_adda'));
        assert.strictEqual(form.$('input[name="foo"]').val(),'MylittleFooValue',
            'shouldcontainthedefaultvalue');

        def=testUtils.makeTestPromise();

        awaittestUtils.fields.many2one.clickOpenDropdown('product_id');
        awaittestUtils.fields.many2one.clickHighlightedItem('product_id');

        //setfoobeforeonchange
        awaittestUtils.fields.editInput(form.$('input[name="foo"]'),"tralala");
        assert.strictEqual(form.$('input[name="foo"]').val(),'tralala',
            'inputshouldcontaintralala');

        //completetheonchange
        def.resolve();
        awaittestUtils.nextTick();

        assert.strictEqual(form.$('input[name="foo"]').val(),'tralala',
            'inputshouldcontainthesamevalueasbeforeonchange');

        form.destroy();
    });

    QUnit.test('inputfield:changevaluebeforependingonchangereturns(withfieldDebounce)',asyncfunction(assert){
        //thistestisexactlythesameasthepreviousone,exceptthatweset
        //hereafieldDebouncetoaccuratelyreproducewhathappensinpractice:
        //thefielddoesn'tnotifythechangeson'input',buton'change'event.
        assert.expect(5);

        this.data.partner.onchanges={
            product_id:function(obj){
                obj.int_field=obj.product_id?7:false;
            },
        };

        letdef;
        constform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:`
                <form>
                    <fieldname="p">
                        <treeeditable="bottom">
                            <fieldname="product_id"/>
                            <fieldname="foo"/>
                            <fieldname="int_field"/>
                        </tree>
                    </field>
                </form>`,
            asyncmockRPC(route,args){
                constresult=this._super(...arguments);
                if(args.method==="onchange"){
                    awaitPromise.resolve(def);
                }
                returnresult;
            },
            fieldDebounce:5000,
        });

        awaittestUtils.dom.click(form.$('.o_field_x2many_list_row_adda'));
        assert.strictEqual(form.$('input[name="foo"]').val(),'MylittleFooValue',
            'shouldcontainthedefaultvalue');

        def=testUtils.makeTestPromise();

        awaittestUtils.fields.many2one.clickOpenDropdown('product_id');
        awaittestUtils.fields.many2one.clickHighlightedItem('product_id');

        //setfoobeforeonchange
        awaittestUtils.fields.editInput(form.$('input[name="foo"]'),"tralala");
        assert.strictEqual(form.$('input[name="foo"]').val(),'tralala');
        assert.strictEqual(form.$('input[name="int_field"]').val(),'');

        //completetheonchange
        def.resolve();
        awaittestUtils.nextTick();

        assert.strictEqual(form.$('input[name="foo"]').val(),'tralala',
            'fooshouldcontainthesamevalueasbeforeonchange');
        assert.strictEqual(form.$('input[name="int_field"]').val(),'7',
            'int_fieldshouldcontainthevaluereturnedbytheonchange');

        form.destroy();
    });

    QUnit.test('inputfield:changevaluebeforependingonchangerenaming',asyncfunction(assert){
        assert.expect(3);

        this.data.partner.onchanges={
            product_id:function(obj){
                obj.foo='onchangevalue';
            },
        };

        vardef=testUtils.makeTestPromise();
        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<form>'+
                    '<sheet>'+
                        '<fieldname="product_id"/>'+
                        '<fieldname="foo"/>'+
                    '</sheet>'+
                '</form>',
            res_id:1,
            mockRPC:function(route,args){
                varresult=this._super.apply(this,arguments);
                if(args.method==="onchange"){
                    returndef.then(function(){
                        returnresult;
                    });
                }else{
                    returnresult;
                }
            },
            viewOptions:{
                mode:'edit',
            },
        });

        assert.strictEqual(form.$('input[name="foo"]').val(),'yop',
            'shouldcontainthecorrectvalue');

        awaittestUtils.fields.many2one.clickOpenDropdown('product_id');
        awaittestUtils.fields.many2one.clickHighlightedItem('product_id');

        //setfoobeforeonchange
        testUtils.fields.editInput(form.$('input[name="foo"]'),"tralala");
        assert.strictEqual(form.$('input[name="foo"]').val(),'tralala',
            'inputshouldcontaintralala');

        //completetheonchange
        def.resolve();
        assert.strictEqual(form.$('input[name="foo"]').val(),'tralala',
            'inputshouldcontainthesamevalueasbeforeonchange');

        form.destroy();
    });

    QUnit.test('inputfield:changepasswordvalue',asyncfunction(assert){
        assert.expect(4);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<form>'+
                    '<fieldname="foo"password="True"/>'+
                '</form>',
            res_id:1,
        });

        assert.notEqual(form.$('.o_field_char').text(),"yop",
            "passwordfieldvalueshouldnotbevisibleinreadmode");
        assert.strictEqual(form.$('.o_field_char').text(),"***",
            "passwordfieldvalueshouldbehiddenwith'*'inreadmode");

        awaittestUtils.form.clickEdit(form);

        assert.hasAttrValue(form.$('input.o_field_char'),'type','password',
            "passwordfieldinputshouldbewithtype'password'ineditmode");
        assert.strictEqual(form.$('input.o_field_char').val(),'yop',
            "passwordfieldinputvalueshouldbethe(non-hidden)passwordvalue");

        form.destroy();
    });

    QUnit.test('inputfield:emptypassword',asyncfunction(assert){
        assert.expect(3);

        this.data.partner.records[0].foo=false;

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<form>'+
                    '<fieldname="foo"password="True"/>'+
                '</form>',
            res_id:1,
        });

        assert.strictEqual(form.$('.o_field_char').text(),"",
            "passwordfieldvalueshouldbeemptyinreadmode");

        awaittestUtils.form.clickEdit(form);

        assert.hasAttrValue(form.$('input.o_field_char'),'type','password',
            "passwordfieldinputshouldbewithtype'password'ineditmode");
        assert.strictEqual(form.$('input.o_field_char').val(),'',
            "passwordfieldinputvalueshouldbethe(non-hidden,empty)passwordvalue");

        form.destroy();
    });

    QUnit.test('inputfield:setandremovevalue,thenwaitforonchange',asyncfunction(assert){
        assert.expect(2);

        this.data.partner.onchanges={
            product_id(obj){
                obj.foo=obj.product_id?"onchangevalue":false;
            },
        };

        letdef;
        constform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:`
                <form>
                    <fieldname="p">
                        <treeeditable="bottom">
                            <fieldname="product_id"/>
                            <fieldname="foo"/>
                        </tree>
                    </field>
                </form>`,
            asyncmockRPC(route,args){
                constresult=this._super(...arguments);
                if(args.method==="onchange"){
                    awaitPromise.resolve(def);
                }
                returnresult;
            },
            fieldDebounce:1000,//neededtoaccuratelymockwhatreallyhappens
        });

        awaittestUtils.dom.click(form.$('.o_field_x2many_list_row_adda'));
        assert.strictEqual(form.$('input[name="foo"]').val(),"");

        awaittestUtils.fields.editInput(form.$('input[name="foo"]'),"test");//setvalueforfoo
        awaittestUtils.fields.editInput(form.$('input[name="foo"]'),"");//removevalueforfoo

        //triggertheonchangebysettingaproduct
        awaittestUtils.fields.many2one.clickOpenDropdown('product_id');
        awaittestUtils.fields.many2one.clickHighlightedItem('product_id');
        assert.strictEqual(form.$('input[name="foo"]').val(),'onchangevalue',
            'inputshouldcontaincorrectvalueafteronchange');

        form.destroy();
    });

    QUnit.module('UrlWidget');

    QUnit.test('urlwidgetinformview',asyncfunction(assert){
        assert.expect(9);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<sheet>'+
                        '<group>'+
                            '<fieldname="foo"widget="url"/>'+
                        '</group>'+
                    '</sheet>'+
                '</form>',
            res_id:1,
        });

        assert.containsOnce(form,'a.o_form_uri.o_field_widget.o_text_overflow',
            "shouldhaveaanchorwithcorrectclasses");
        assert.hasAttrValue(form.$('a.o_form_uri.o_field_widget.o_text_overflow'),'href','http://yop',
            "shouldhaveproperhreflink");
        assert.hasAttrValue(form.$('a.o_form_uri.o_field_widget.o_text_overflow'),'target','_blank',
            "shouldhavetargetattributesetto_blank");
        assert.strictEqual(form.$('a.o_form_uri.o_field_widget.o_text_overflow').text(),'yop',
            "thevalueshouldbedisplayedproperly");

        //switchtoeditmodeandchecktheresult
        awaittestUtils.form.clickEdit(form);
        assert.containsOnce(form,'input[type="text"].o_field_widget',
            "shouldhaveaninputforthecharfield");
        assert.strictEqual(form.$('input[type="text"].o_field_widget').val(),'yop',
            "inputshouldcontainfieldvalueineditmode");

        //changevalueineditmode
        testUtils.fields.editInput(form.$('input[type="text"].o_field_widget'),'limbo');

        //save
        awaittestUtils.form.clickSave(form);
        assert.containsOnce(form,'a.o_form_uri.o_field_widget.o_text_overflow',
            "shouldstillhaveaanchorwithcorrectclasses");
        assert.hasAttrValue(form.$('a.o_form_uri.o_field_widget.o_text_overflow'),'href','http://limbo',
            "shouldhavepropernewhreflink");
        assert.strictEqual(form.$('a.o_form_uri.o_field_widget.o_text_overflow').text(),'limbo',
            'thenewvalueshouldbedisplayed');

        form.destroy();
    });

    QUnit.test('urlwidgettakestextfromproperattribute',asyncfunction(assert){
        assert.expect(1);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<fieldname="foo"widget="url"text="kebeclibre"/>'+
                '</form>',
            res_id:1,
        });

        assert.strictEqual(form.$('a[name="foo"]').text(),'kebeclibre',
            "urltextshouldcomefromthetextattribute");
        form.destroy();
    });

    QUnit.test('urlwidget:hrefattributeandwebsite_pathoption',asyncfunction(assert){
        assert.expect(4);

        this.data.partner.fields.url1={string:"Url1",type:"char",default:"www.url1.com"};
        this.data.partner.fields.url2={string:"Url2",type:"char",default:"www.url2.com"};
        this.data.partner.fields.url3={string:"Url3",type:"char",default:"http://www.url3.com"};
        this.data.partner.fields.url4={string:"Url4",type:"char",default:"https://url4.com"};

        constform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:`
                <form>
                    <fieldname="url1"widget="url"/>
                    <fieldname="url2"widget="url"options="{'website_path':True}"/>
                    <fieldname="url3"widget="url"/>
                    <fieldname="url4"widget="url"/>
                </form>`,
            res_id:1,
        });

        assert.strictEqual(form.$('a[name="url1"]').attr('href'),'http://www.url1.com');
        assert.strictEqual(form.$('a[name="url2"]').attr('href'),'www.url2.com');
        assert.strictEqual(form.$('a[name="url3"]').attr('href'),'http://www.url3.com');
        assert.strictEqual(form.$('a[name="url4"]').attr('href'),'https://url4.com');

        form.destroy();
    });

    QUnit.test('charfieldineditablelistview',asyncfunction(assert){
        assert.expect(10);

        varlist=awaitcreateView({
            View:ListView,
            model:'partner',
            data:this.data,
            arch:'<treeeditable="bottom"><fieldname="foo"widget="url"/></tree>',
        });

        assert.strictEqual(list.$('tbodytd:not(.o_list_record_selector)').length,5,
            "shouldhave5cells");
        assert.containsN(list,'a.o_form_uri.o_field_widget.o_text_overflow',5,
            "shouldhave5anchorswithcorrectclasses");
        assert.hasAttrValue(list.$('a.o_form_uri.o_field_widget.o_text_overflow').first(),'href','http://yop',
            "shouldhaveproperhreflink");
        assert.strictEqual(list.$('tbodytd:not(.o_list_record_selector)').first().text(),'yop',
            "valueshouldbedisplayedproperlyastext");

        //Editalineandchecktheresult
        var$cell=list.$('tbodytd:not(.o_list_record_selector)').first();
        awaittestUtils.dom.click($cell);
        assert.hasClass($cell.parent(),'o_selected_row','shouldbesetaseditmode');
        assert.strictEqual($cell.find('input').val(),'yop',
            'shouldhavethecorectvalueininternalinput');
        awaittestUtils.fields.editInput($cell.find('input'),'brolo');

        //save
        awaittestUtils.dom.click(list.$buttons.find('.o_list_button_save'));
        $cell=list.$('tbodytd:not(.o_list_record_selector)').first();
        assert.doesNotHaveClass($cell.parent(),'o_selected_row','shouldnotbeineditmodeanymore');
        assert.containsN(list,'a.o_form_uri.o_field_widget.o_text_overflow',5,
            "shouldstillhave5anchorswithcorrectclasses");
        assert.hasAttrValue(list.$('a.o_form_uri.o_field_widget.o_text_overflow').first(),'href','http://brolo',
            "shouldhavepropernewhreflink");
        assert.strictEqual(list.$('a.o_form_uri.o_field_widget.o_text_overflow').first().text(),'brolo',
            "valueshouldbeproperlyupdated");

        list.destroy();
    });

    QUnit.module('CopyClipboard');

    QUnit.test('Char&TextFields:Copytoclipboardbutton',asyncfunction(assert){
        assert.expect(2);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<sheet>'+
                            '<div>'+
                                '<fieldname="txt"widget="CopyClipboardText"/>'+
                                '<fieldname="foo"widget="CopyClipboardChar"/>'+
                            '</div>'+
                    '</sheet>'+
                '</form>',
            res_id:1,
        });

        assert.containsOnce(form,'.o_clipboard_button.o_btn_text_copy',"Shouldhavecopybuttonontexttypefield");
        assert.containsOnce(form,'.o_clipboard_button.o_btn_char_copy',"Shouldhavecopybuttononchartypefield");

        form.destroy();
    });

    QUnit.test('CopyClipboardwidgetonunsetfield',asyncfunction(assert){
        assert.expect(1);

        this.data.partner.records[0].foo=false;

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<form>'+
                    '<sheet>'+
                        '<group>'+
                            '<fieldname="foo"widget="CopyClipboardChar"/>'+
                        '</group>'+
                    '</sheet>'+
                '</form>',
            res_id:1,
        });

        assert.containsNone(form,'.o_field_copy[name="foo"].o_clipboard_button',
            "foo(unset)shouldnotcontainabutton");

        form.destroy();
    });

    QUnit.test('CopyClipboardwidgetonreadonlyunsetfieldsincreatemode',asyncfunction(assert){
        assert.expect(1);

        this.data.partner.fields.display_name.readonly=true;

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<form>'+
                    '<sheet>'+
                        '<group>'+
                            '<fieldname="display_name"widget="CopyClipboardChar"/>'+
                        '</group>'+
                    '</sheet>'+
                '</form>',
        });

        assert.containsNone(form,'.o_field_copy[name="display_name"].o_clipboard_button',
            "thereadonlyunsetfieldshouldnotcontainabutton");

        form.destroy();
    });

    QUnit.module('FieldText');

    QUnit.test('textfieldsarecorrectlyrendered',asyncfunction(assert){
        assert.expect(7);

        this.data.partner.fields.foo.type='text';
        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<fieldname="int_field"/>'+
                    '<fieldname="foo"/>'+
                '</form>',
            res_id:1,
        });

        assert.ok(form.$('.o_field_text').length,"shouldhaveatextarea");
        assert.strictEqual(form.$('.o_field_text').text(),'yop','shouldbe"yop"inreadonly');

        awaittestUtils.form.clickEdit(form);

        var$textarea=form.$('textarea.o_field_text');
        assert.ok($textarea.length,"shouldhaveatextarea");
        assert.strictEqual($textarea.val(),'yop','shouldstillbe"yop"inedit');

        testUtils.fields.editInput($textarea,'hello');
        assert.strictEqual($textarea.val(),'hello','shouldbe"hello"afterfirstedition');

        testUtils.fields.editInput($textarea,'helloworld');
        assert.strictEqual($textarea.val(),'helloworld','shouldbe"helloworld"aftersecondedition');

        awaittestUtils.form.clickSave(form);

        assert.strictEqual(form.$('.o_field_text').text(),'helloworld',
            'shouldbe"helloworld"aftersave');
        form.destroy();
    });

    QUnit.test('textfieldsineditmodehavecorrectheight',asyncfunction(assert){
        assert.expect(2);

        this.data.partner.fields.foo.type='text';
        this.data.partner.records[0].foo="f\nu\nc\nk\nm\ni\nl\ng\nr\no\nm";
        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<fieldname="foo"/>'+
                '</form>',
            res_id:1,
        });

        var$field=form.$('.o_field_text');

        assert.strictEqual($field[0].offsetHeight,$field[0].scrollHeight,
            "textfieldshouldnothaveascrollbar");

        awaittestUtils.form.clickEdit(form);

        var$textarea=form.$('textarea:first');

        //thedifferenceistotakesmallcalculationerrorsintoaccount
        assert.strictEqual($textarea[0].clientHeight,$textarea[0].scrollHeight,
            "textareashouldnothaveascrollbar");
        form.destroy();
    });

    QUnit.test('textfieldsineditmode,noverticalresize',asyncfunction(assert){
        assert.expect(1);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<fieldname="txt"/>'+
                '</form>',
            res_id:1,
        });

        awaittestUtils.form.clickEdit(form);

        var$textarea=form.$('textarea:first');

        assert.strictEqual($textarea.css('resize'),'none',
            "shouldnothaveverticalresize");

        form.destroy();
    });

    QUnit.test('textfieldsshouldhavecorrectheightafteronchange',asyncfunction(assert){
        assert.expect(2);

        constdamnLongText=`Loremipsumdolorsitamet,consecteturadipiscingelit.
            Donecestmassa,gravidaegetdapibusac,eleifendegetlibero.
            Suspendissefeugiatsedmassaeleifendvestibulum.Sedtincidunt
            velitsedlacinialacinia.Nuncinfermentumnunc.Vestibulumante
            ipsumprimisinfaucibusorciluctusetultricesposuerecubilia
            Curae;Nullamutnisiaestornaremolestienonvulputateorci.
            Nuncpharetraportasemper.Maurisdictumeunullaapulvinar.Duis
            eleifendodioidligulaconguesollicitudin.Curabiturquisaliquet
            nunc,utaliquetenim.Suspendissemalesuadafelisnonmetus
            efficituraliquet.`;

        this.data.partner.records[0].txt=damnLongText;
        this.data.partner.records[0].bar=false;
        this.data.partner.onchanges={
            bar:function(obj){
                obj.txt=damnLongText;
            },
        };
        constform=awaitcreateView({
            arch:`
                <formstring="Partners">
                    <fieldname="bar"/>
                    <fieldname="txt"attrs="{'invisible':[('bar','=',True)]}"/>
                </form>`,
            data:this.data,
            model:'partner',
            res_id:1,
            View:FormView,
            viewOptions:{mode:'edit'},
        });

        consttextarea=form.el.querySelector('textarea[name="txt"]');
        constinitialHeight=textarea.offsetHeight;

        awaittestUtils.fields.editInput($(textarea),'Shortvalue');

        assert.ok(textarea.offsetHeight<initialHeight,
            "Textareaheightshouldhaveshrank");

        awaittestUtils.dom.click(form.$('.o_field_boolean[name="bar"]input'));
        awaittestUtils.dom.click(form.$('.o_field_boolean[name="bar"]input'));

        assert.strictEqual(textarea.offsetHeight,initialHeight,
            "Textareaheightshouldbereset");

        form.destroy();
    });

    QUnit.test('textfieldsineditablelisthavecorrectheight',asyncfunction(assert){
        assert.expect(2);

        this.data.partner.records[0].txt="a\nb\nc\nd\ne\nf";

        varlist=awaitcreateView({
            View:ListView,
            model:'partner',
            data:this.data,
            arch:'<listeditable="top">'+
                    '<fieldname="foo"/>'+
                    '<fieldname="txt"/>'+
                '</list>',
        });

        //Clicktoenteredit:inthistestwespecificallydonotset
        //thefocusonthetextareabyclickingonanothercolumn.
        //Themaingoalistotesttheresizeisactuallytriggeredinthis
        //particularcase.
        awaittestUtils.dom.click(list.$('.o_data_cell:first'));
        var$textarea=list.$('textarea:first');

        //makesurethecorrectdataisthere
        assert.strictEqual($textarea.val(),this.data.partner.records[0].txt);

        //makesurethereisnoscrollbar
        assert.strictEqual($textarea[0].clientHeight,$textarea[0].scrollHeight,
            "textareashouldnothaveascrollbar");

        list.destroy();
    });

    QUnit.test('textfieldsineditmodeshouldresizeonreset',asyncfunction(assert){
        assert.expect(1);

        this.data.partner.fields.foo.type='text';

        this.data.partner.onchanges={
            bar:function(obj){
                obj.foo='a\nb\nc\nd\ne\nf';
            },
        };

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<fieldname="bar"/>'+
                    '<fieldname="foo"/>'+
                '</form>',
            res_id:1,
        });

        //edittheform
        //triggeratextareareset(throughonchange)byclickingthebox
        //thencheckthereisnoscrollbar
        awaittestUtils.form.clickEdit(form);

        awaittestUtils.dom.click(form.$('div[name="bar"]input'));

        var$textarea=form.$('textarea:first');
        assert.strictEqual($textarea.innerHeight(),$textarea[0].scrollHeight,
            "textareashouldnothaveascrollbar");

        form.destroy();
    });

    QUnit.test('textfieldtranslatable',asyncfunction(assert){
        assert.expect(3);

        this.data.partner.fields.txt.translate=true;

        varmultiLang=_t.database.multi_lang;
        _t.database.multi_lang=true;

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<sheet>'+
                        '<group>'+
                            '<fieldname="txt"/>'+
                        '</group>'+
                    '</sheet>'+
                '</form>',
            res_id:1,
            mockRPC:function(route,args){
                if(route==="/web/dataset/call_button"&&args.method==='translate_fields'){
                    assert.deepEqual(args.args,["partner",1,"txt"],'shouldcall"call_button"route');
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
        var$button=form.$('textarea+.o_field_translate');
        assert.strictEqual($button.length,1,"shouldhaveatranslatebutton");
        awaittestUtils.dom.click($button);
        assert.containsOnce($(document),'.modal','thereshouldbeatranslationmodal');
        form.destroy();
        _t.database.multi_lang=multiLang;
    });

    QUnit.test('textfieldtranslatableincreatemode',asyncfunction(assert){
        assert.expect(1);

        this.data.partner.fields.txt.translate=true;

        varmultiLang=_t.database.multi_lang;
        _t.database.multi_lang=true;
        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<sheet>'+
                        '<group>'+
                            '<fieldname="txt"/>'+
                        '</group>'+
                    '</sheet>'+
                '</form>',
        });
        var$button=form.$('textarea+.o_field_translate');
        assert.strictEqual($button.length,1,"shouldhaveatranslatebuttonincreatemode");
        form.destroy();

        _t.database.multi_lang=multiLang;
    });

    QUnit.test('gotonextline(andnotthenextrow)whenpressingenter',asyncfunction(assert){
        assert.expect(4);

        this.data.partner.fields.foo.type='text';
        varlist=awaitcreateView({
            View:ListView,
            model:'partner',
            data:this.data,
            arch:'<listeditable="top">'+
                    '<fieldname="int_field"/>'+
                    '<fieldname="foo"/>'+
                    '<fieldname="qux"/>'+
                '</list>',
        });

        awaittestUtils.dom.click(list.$('tbodytr:first.o_list_text'));
        var$textarea=list.$('textarea.o_field_text');
        assert.strictEqual($textarea.length,1,"shouldhaveatextarea");
        assert.strictEqual($textarea.val(),'yop','shouldstillbe"yop"inedit');

        assert.strictEqual(list.$('textarea').get(0),document.activeElement,
            "textareashouldhavethefocus");

        //clickonenter
        list.$('textarea')
            .trigger({type:"keydown",which:$.ui.keyCode.ENTER})
            .trigger({type:"keyup",which:$.ui.keyCode.ENTER});

        assert.strictEqual(list.$('textarea').first().get(0),document.activeElement,
            "textareashouldstillhavethefocus");

        list.destroy();
    });

    //Firefox-specific
    //Copyingfrom<divstyle="white-space:pre-wrap">doesnotkeeplinebreaks
    //Seehttps://bugzilla.mozilla.org/show_bug.cgi?id=1390115
    QUnit.test('copyingtextfieldsinROmodeshouldpreservelinebreaks',asyncfunction(assert){
        assert.expect(1);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<sheet>'+
                        '<group>'+
                            '<fieldname="txt"/>'+
                        '</group>'+
                    '</sheet>'+
                '</form>',
            res_id:1,
        });

        //Copyingfromadivtagwithwhite-space:pre-wrapdoesn'tworkinFirefox
        assert.strictEqual(form.$('[name="txt"]').prop("tagName").toLowerCase(),'span',
            "thefieldcontentsshouldbesurroundedbyaspantag");

        form.destroy();
    });

    QUnit.module('FieldBinary');

    QUnit.test('binaryfieldsarecorrectlyrendered',asyncfunction(assert){
        assert.expect(16);

        //savethesessionfunction
        varoldGetFile=session.get_file;
        session.get_file=function(option){
            assert.strictEqual(option.data.field,'document',
                "weshoulddownloadthefielddocument");
            assert.strictEqual(option.data.data,'coucou==\n',
                "weshoulddownloadthecorrectdata");
            option.complete();
            returnPromise.resolve();
        };

        this.data.partner.records[0].foo='coucou.txt';
        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<fieldname="document"filename="foo"/>'+
                    '<fieldname="foo"/>'+
                '</form>',
            res_id:1,
        });

        assert.containsOnce(form,'a.o_field_widget[name="document"]>.fa-download',
            "thebinaryfieldshouldberenderedasadownloadablelinkinreadonly");
        assert.strictEqual(form.$('a.o_field_widget[name="document"]').text().trim(),'coucou.txt',
            "thebinaryfieldshoulddisplaythenameofthefileinthelink");
        assert.strictEqual(form.$('.o_field_char').text(),'coucou.txt',
            "thefilenamefieldshouldhavethefilenameasvalue");

        awaittestUtils.dom.click(form.$('a.o_field_widget[name="document"]'));

        awaittestUtils.form.clickEdit(form);

        assert.containsNone(form,'a.o_field_widget[name="document"]>.fa-download',
            "thebinaryfieldshouldnotberenderedasadownloadablelinkinedit");
        assert.strictEqual(form.$('div.o_field_binary_file[name="document"]>input').val(),'coucou.txt',
            "thebinaryfieldshoulddisplaythefilenameintheinputeditmode");
        assert.hasAttrValue(form.$('.o_field_binary_file>input'),'readonly','readonly',
            "theinputshouldbereadonly");
        assert.containsOnce(form,'.o_field_binary_file>.o_clear_file_button',
            "thereshoudbeabuttontoclearthefile");
        assert.strictEqual(form.$('input.o_field_char').val(),'coucou.txt',
            "thefilenamefieldshouldhavethefilenameasvalue");


        awaittestUtils.dom.click(form.$('.o_field_binary_file>.o_clear_file_button'));

        assert.isNotVisible(form.$('.o_field_binary_file>input'),
            "theinputshouldbehidden");
        assert.strictEqual(form.$('.o_field_binary_file>.o_select_file_button:not(.o_hidden)').length,1,
            "thereshoudbeabuttontouploadthefile");
        assert.strictEqual(form.$('input.o_field_char').val(),'',
            "thefilenamefieldshouldbeemptysinceweremovedthefile");

        awaittestUtils.form.clickSave(form);
        assert.containsNone(form,'a.o_field_widget[name="document"]>.fa-download',
            "thebinaryfieldshouldnotrenderasadownloadablelinksinceweremovedthefile");
        assert.strictEqual(form.$('a.o_field_widget[name="document"]').text().trim(),'',
            "thebinaryfieldshouldnotdisplayafilenameinthelinksinceweremovedthefile");
        assert.strictEqual(form.$('.o_field_char').text().trim(),'',
            "thefilenamefieldshouldbeemptysinceweremovedthefile");

        form.destroy();

        //restorethesessionfunction
        session.get_file=oldGetFile;
    });

    QUnit.test('binaryfields:optionaccepted_file_extensions',asyncfunction(assert){
        assert.expect(1);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:`<formstring="Partners">
                      <fieldname="document"widget="binary"options="{'accepted_file_extensions':'.dat,.bin'}"/>
                   </form>`
        });
        assert.strictEqual(form.$('input.o_input_file').attr('accept'),'.dat,.bin',
            "theinputshouldhavethecorrect``accept``attribute");
        form.destroy();
    });

    QUnit.test('binaryfieldsthatarereadonlyincreatemodedonotdownload',asyncfunction(assert){
        assert.expect(4);

        //savethesessionfunction
        varoldGetFile=session.get_file;
        session.get_file=function(option){
            assert.step('Weshouldn\'tbegettingthefile.');
            returnoldGetFile.bind(session)(option);
        };

        this.data.partner.onchanges={
            product_id:function(obj){
                obj.document="onchange==\n";
            },
        };

        this.data.partner.fields.document.readonly=true;

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<fieldname="product_id"/>'+
                    '<fieldname="document"filename="\'yooo\'"/>'+
                '</form>',
            res_id:1,
        });

        awaittestUtils.form.clickCreate(form);
        awaittestUtils.fields.many2one.clickOpenDropdown('product_id');
        awaittestUtils.fields.many2one.clickHighlightedItem('product_id');

        assert.containsOnce(form,'a.o_field_widget[name="document"]',
            'Thelinktodownloadthebinaryshouldbepresent');
        assert.containsNone(form,'a.o_field_widget[name="document"]>.fa-download',
            'Thedownloadiconshouldnotbepresent');

        varlink=form.$('a.o_field_widget[name="document"]');
        assert.ok(link.is(':hidden'),"thelinkelementshouldnotbevisible");

        //forcevisibilitytotestthattheclickinghasalsobeendisabled
        link.removeClass('o_hidden');
        testUtils.dom.click(link);

        assert.verifySteps([]);//Weshouldn'thavepassedthroughsteps

        form.destroy();
        session.get_file=oldGetFile;
    });

    QUnit.module('FieldPdfViewer');

    QUnit.test("pdf_viewerwithoutdata",asyncfunction(assert){
        assert.expect(4);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:
                '<form>'+
                    '<fieldname="document"widget="pdf_viewer"/>'+
                '</form>',
        });

        assert.hasClass(form.$('.o_field_widget'),'o_field_pdfviewer');
        assert.strictEqual(form.$('.o_select_file_button:not(.o_hidden)').length,1,
            "thereshouldbeavisible'Upload'button");
        assert.isNotVisible(form.$('.o_field_widgetiframe.o_pdfview_iframe'),
            "thereshouldbeaninvisibleiframe");
        assert.containsOnce(form,'input[type="file"]',
            "thereshouldbeoneinput");

        form.destroy();
    });

    QUnit.test("pdf_viewer:basicrendering",asyncfunction(assert){
        assert.expect(4);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            res_id:1,
            arch:
                '<form>'+
                    '<fieldname="document"widget="pdf_viewer"/>'+
                '</form>',
            mockRPC:function(route){
                if(route.indexOf('/web/static/lib/pdfjs/web/viewer.html')!==-1){
                    returnPromise.resolve();
                }
                returnthis._super.apply(this,arguments);
            }
        });

        assert.hasClass(form.$('.o_field_widget'),'o_field_pdfviewer');
        assert.strictEqual(form.$('.o_select_file_button:not(.o_hidden)').length,0,
            "thereshouldnotbeaanyvisible'Upload'button");
        assert.isVisible(form.$('.o_field_widgetiframe.o_pdfview_iframe'),
            "thereshouldbeanvisibleiframe");
        assert.hasAttrValue(form.$('.o_field_widgetiframe.o_pdfview_iframe'),'data-src',
            '/web/static/lib/pdfjs/web/viewer.html?file=%2Fweb%2Fcontent%3Fmodel%3Dpartner%26field%3Ddocument%26id%3D1#page=1',
            "thesrcattributeshouldbecorrectlysetontheiframe");

        form.destroy();
    });

    QUnit.test("pdf_viewer:uploadrendering",asyncfunction(assert){
        assert.expect(6);

        testUtils.mock.patch(field_registry.map.pdf_viewer,{
            on_file_change:function(ev){
                ev.target={files:[newBlob()]};
                this._super.apply(this,arguments);
            },
            _getURI:function(fileURI){
                this._super.apply(this,arguments);
                assert.step('_getURI');
                assert.ok(_.str.startsWith(fileURI,'blob:'));
                this.PDFViewerApplication={
                    open:function(URI){
                        assert.step('open');
                        assert.ok(_.str.startsWith(URI,'blob:'));
                    },
                };
                return'about:blank';
            },
        });

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:
                '<form>'+
                    '<fieldname="document"widget="pdf_viewer"/>'+
                '</form>',
        });

        //firstuploadinitializeiframe
        form.$('input[type="file"]').trigger('change');
        assert.verifySteps(['_getURI']);
        //seconduploadcallpdfjsmethodinsideiframe
        form.$('input[type="file"]').trigger('change');
        assert.verifySteps(['open']);

        testUtils.mock.unpatch(field_registry.map.pdf_viewer);
        form.destroy();
    });

    QUnit.test('textfieldrenderinginlistview',asyncfunction(assert){
        assert.expect(1);

        vardata={
            foo:{
                fields:{foo:{string:"F",type:"text"}},
                records:[{id:1,foo:"sometext"}]
            },
        };
        varlist=awaitcreateView({
            View:ListView,
            model:'foo',
            data:data,
            arch:'<tree><fieldname="foo"/></tree>',
        });

        assert.strictEqual(list.$('tbodytd.o_list_text:contains(sometext)').length,1,
            "shouldhaveatdwiththe.o_list_textclass");
        list.destroy();
    });

    QUnit.test("binaryfieldsinputvalueisemptywheanclearingafteruploading",asyncfunction(assert){
        assert.expect(2);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                '<fieldname="document"filename="foo"/>'+
                '<fieldname="foo"/>'+
                '</form>',
            res_id:1,
        });

        awaittestUtils.form.clickEdit(form);

        ////Weneedtoconverttheinputtypesincewecan'tprogrammaticallysetthevalueofafileinput
        form.$('.o_input_file').attr('type','text').val('coucou.txt');

        assert.strictEqual(form.$('.o_input_file').val(),'coucou.txt',
            "inputvalueshouldbechangedto\"coucou.txt\"");

        awaittestUtils.dom.click(form.$('.o_field_binary_file>.o_clear_file_button'));

        assert.strictEqual(form.$('.o_input_file').val(),'',
            "inputvalueshouldbeempty");

        form.destroy();
    });

    QUnit.test('fieldtextineditablelistview',asyncfunction(assert){
        assert.expect(1);

        this.data.partner.fields.foo.type='text';

        varlist=awaitcreateView({
            View:ListView,
            model:'partner',
            data:this.data,
            arch:'<treestring="Phonecalls"editable="top">'+
                    '<fieldname="foo"/>'+
                '</tree>',
        });

        awaittestUtils.dom.click(list.$buttons.find('.o_list_button_add'));

        assert.strictEqual(list.$('textarea').first().get(0),document.activeElement,
            "textareashouldhavethefocus");
        list.destroy();
    });

    QUnit.module('FieldImage');

    QUnit.test('imagefieldsarecorrectlyrendered',asyncfunction(assert){
        assert.expect(7);

        this.data.partner.records[0].__last_update='2017-02-0810:00:00';
        this.data.partner.records[0].document=MY_IMAGE;

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<fieldname="document"widget="image"options="{\'size\':[90,90]}"/>'+
                '</form>',
            res_id:1,
            asyncmockRPC(route,args){
                if(route==='/web/dataset/call_kw/partner/read'){
                    assert.deepEqual(args.args[1],['document','__last_update','display_name'],"Thefieldsdocument,display_nameand__last_updateshouldbepresentwhenreadinganimage");
                }
                if(route===`data:image/png;base64,${MY_IMAGE}`){
                    assert.ok(true,"shouldcalledthecorrectroute");
                    return'wow';
                }
                returnthis._super.apply(this,arguments);
            },
        });

        assert.hasClass(form.$('div[name="document"]'),'o_field_image',
            "thewidgetshouldhavethecorrectclass");
        assert.containsOnce(form,'div[name="document"]>img',
            "thewidgetshouldcontainanimage");
        assert.hasClass(form.$('div[name="document"]>img'),'img-fluid',
            "theimageshouldhavethecorrectclass");
        assert.hasAttrValue(form.$('div[name="document"]>img'),'width',"90",
            "theimageshouldcorrectlysetitsattributes");
        assert.strictEqual(form.$('div[name="document"]>img').css('max-width'),"90px",
            "theimageshouldcorrectlysetitsattributes");
        form.destroy();
    });

    QUnit.test('imagefieldsarecorrectlyrenderedwithonedimensionset',asyncfunction(assert){
        assert.expect(6);

        this.data.partner.fields.picture={string:'Picture',type:'binary'};
        this.data.partner.records[0].__last_update='2017-02-0810:00:00';
        this.data.partner.records[0].document='myimage1';
        this.data.partner.records[0].picture='myimage2';

        constform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                '<fieldname="document"widget="image"options="{\'size\':[180,0]}"/>'+
                '<fieldname="picture"widget="image"options="{\'size\':[0,270]}"/>'+
                '</form>',
            res_id:1,
            mockRPC:function(route,args){
                if(route.startsWith('data:image/png;base64,myimage')){
                    returnPromise.resolve('wow');
                }
                returnthis._super.apply(this,arguments);
            },
        });

        assert.containsOnce(form,'div[name="document"]>img',"thewidgetshouldcontainanimage");
        assert.hasAttrValue(form.$('div[name="document"]>img'),'width',"180",
            "theimageshouldcorrectlysetitsattributes");
        constimage1Style=form.$('div[name="document"]>img').attr('style');
        assert.ok(['max-width:180px','height:auto','max-height:100%'].every(e=>image1Style.includes(e)),
            "theimageshouldcorrectlysetitsstyle");

        assert.containsOnce(form,'div[name="picture"]>img',"thewidgetshouldcontainanimage");
        assert.hasAttrValue(form.$('div[name="picture"]>img'),'height',"270",
            "theimageshouldcorrectlysetitsattributes");
        constimage2Style=form.$('div[name="picture"]>img').attr('style');
        assert.ok(['max-height:270px','width:auto','max-width:100%'].every(e=>image2Style.includes(e)),
            "theimageshouldcorrectlysetitsstyle");

        form.destroy();
    });

    QUnit.test('imagefieldsarecorrectlyreplacedwhengivenanincorrectvalue',asyncfunction(assert){
        assert.expect(7);

        this.data.partner.records[0].__last_update='2017-02-0810:00:00';
        this.data.partner.records[0].document='incorrect_base64_value';

        testUtils.mock.patch(basicFields.FieldBinaryImage,{
            //Delaythe_renderfunction:thiswillensurethattheerrortriggered
            //bytheincorrectbase64valueisdispatchedbeforethesrcisreplaced
            //(seetest_utils_mock.removeSrcAttribute),sincethatfunctioniscalled
            //whentheelementisinsertedintotheDOM.
            async_render(){
                constresult=this._super.apply(this,arguments);
                awaitconcurrency.delay(100);
                returnresult;
            },
        });

        constform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:`
                <formstring="Partners">
                    <fieldname="document"widget="image"options="{'size':[90,90]}"/>
                </form>`,
            res_id:1,
            asyncmockRPC(route,args){
                const_super=this._super;
                if(route==='/web/static/src/img/placeholder.png'){
                    assert.step('callplaceholderroute');
                }
                return_super.apply(this,arguments);
            },
        });

        assert.hasClass(form.$('div[name="document"]'),'o_field_image',
            "thewidgetshouldhavethecorrectclass");
        assert.containsOnce(form,'div[name="document"]>img',
            "thewidgetshouldcontainanimage");
        assert.hasClass(form.$('div[name="document"]>img'),'img-fluid',
            "theimageshouldhavethecorrectclass");
        assert.hasAttrValue(form.$('div[name="document"]>img'),'width',"90",
            "theimageshouldcorrectlysetitsattributes");
        assert.strictEqual(form.$('div[name="document"]>img').css('max-width'),"90px",
            "theimageshouldcorrectlysetitsattributes");

        assert.verifySteps(['callplaceholderroute']);

        form.destroy();
        testUtils.mock.unpatch(basicFields.FieldBinaryImage);
    });

    QUnit.test('image:optionaccepted_file_extensions',asyncfunction(assert){
        assert.expect(2);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:`<formstring="Partners">
                      <fieldname="document"widget="image"options="{'accepted_file_extensions':'.png,.jpeg'}"/>
                   </form>`
        });
        assert.strictEqual(form.$('input.o_input_file').attr('accept'),'.png,.jpeg',
            "theinputshouldhavethecorrect``accept``attribute");
        form.destroy();

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:`<formstring="Partners">
                      <fieldname="document"widget="image"/>
                   </form>`
        });
        assert.strictEqual(form.$('input.o_input_file').attr('accept'),'image/*',
            'thedefaultvaluefortheattribute"accept"onthe"image"widgetmustbe"image/*"');
        form.destroy();
    });

    QUnit.test('imagefieldsinsubviewsareloadedcorrectly',asyncfunction(assert){
        assert.expect(6);

        this.data.partner.records[0].__last_update='2017-02-0810:00:00';
        this.data.partner.records[0].document=MY_IMAGE;
        this.data.partner_type.fields.image={name:'image',type:'binary'};
        this.data.partner_type.records[0].image=PRODUCT_IMAGE;
        this.data.partner.records[0].timmy=[12];

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<fieldname="document"widget="image"options="{\'size\':[90,90]}"/>'+
                    '<fieldname="timmy"widget="many2many">'+
                        '<tree>'+
                            '<fieldname="display_name"/>'+
                        '</tree>'+
                        '<form>'+
                            '<fieldname="image"widget="image"/>'+
                        '</form>'+
                    '</field>'+
                '</form>',
            res_id:1,
            asyncmockRPC(route){
                if(route===`data:image/png;base64,${MY_IMAGE}`){
                    assert.step("Theview'simageshouldhavebeenfetched");
                    return'wow';
                }
                if(route===`data:image/gif;base64,${PRODUCT_IMAGE}`){
                    assert.step("Thedialog'simageshouldhavebeenfetched");
                    return;
                }
                returnthis._super.apply(this,arguments);
            },
        });
        assert.verifySteps(["Theview'simageshouldhavebeenfetched"]);

        assert.containsOnce(form,'tr.o_data_row',
            'Thereshouldbeonerecordinthemany2many');

        //Actualflow:clickonanelementofthem2mtogetitsformview
        awaittestUtils.dom.click(form.$('tbodytd:contains(gold)'));
        assert.strictEqual($('.modal').length,1,
            'Themodalshouldhaveopened');
        assert.verifySteps(["Thedialog'simageshouldhavebeenfetched"]);

        form.destroy();
    });

    QUnit.test('imagefieldsinx2manylistareloadedcorrectly',asyncfunction(assert){
        assert.expect(2);

        this.data.partner_type.fields.image={name:'image',type:'binary'};
        this.data.partner_type.records[0].image=PRODUCT_IMAGE;
        this.data.partner.records[0].timmy=[12];

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<fieldname="timmy"widget="many2many">'+
                        '<tree>'+
                            '<fieldname="image"widget="image"/>'+
                        '</tree>'+
                    '</field>'+
                '</form>',
            res_id:1,
            asyncmockRPC(route){
                if(route===`data:image/gif;base64,${PRODUCT_IMAGE}`){
                    assert.ok(true,"Thelist'simageshouldhavebeenfetched");
                    return;
                }
                returnthis._super.apply(this,arguments);
            },
        });

        assert.containsOnce(form,'tr.o_data_row',
            'Thereshouldbeonerecordinthemany2many');

        form.destroy();
    });

    QUnit.test('imagefieldswithrequiredattribute',asyncfunction(assert){
        assert.expect(2);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<fieldname="document"required="1"widget="image"/>'+
                '</form>',
            mockRPC:function(route,args){
                if(args.method==='create'){
                    thrownewError("ShouldnotdoacreateRPCwithunsetrequiredimagefield");
                }
                returnthis._super.apply(this,arguments);
            },
        });

        awaittestUtils.form.clickSave(form);

        assert.hasClass(form.$('.o_form_view'),'o_form_editable',
            "formviewshouldstillbeeditable");
        assert.hasClass(form.$('.o_field_widget'),'o_field_invalid',
            "imagefieldshouldbedisplayedasinvalid");

        form.destroy();
    });

    /**
     *SameteststhanforImagefields,butforCharfieldswithimage_urlwidget.
     */
    QUnit.module('FieldChar-ImageUrlWidget',{
        beforeEach:function(){
            //specificsixthpartnerdataforimage_urlwidgettests
            this.data.partner.records.push({id:6,bar:false,foo:FR_FLAG_URL,int_field:5,qux:0.0,timmy:[]});
        },
    });

    QUnit.test('imagefieldsarecorrectlyrendered',asyncfunction(assert){
        assert.expect(6);

        constform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<fieldname="foo"widget="image_url"options="{\'size\':[90,90]}"/>'+
                '</form>',
            res_id:6,
            asyncmockRPC(route,args){
                if(route===FR_FLAG_URL){
                    assert.ok(true,"thecorrectrouteshouldhavebeencalled.");
                }
                returnthis._super.apply(this,arguments);
            },
        });

        assert.hasClass(form.$('div[name="foo"]'),'o_field_image',
            "thewidgetshouldhavethecorrectclass");
        assert.containsOnce(form,'div[name="foo"]>img',
            "thewidgetshouldcontainanimage");
        assert.hasClass(form.$('div[name="foo"]>img'),'img-fluid',
            "theimageshouldhavethecorrectclass");
        assert.hasAttrValue(form.$('div[name="foo"]>img'),'width',"90",
            "theimageshouldcorrectlysetitsattributes");
        assert.strictEqual(form.$('div[name="foo"]>img').css('max-width'),"90px",
            "theimageshouldcorrectlysetitsattributes");
        form.destroy();
    });

    QUnit.test('imagefieldsarecorrectlyrenderedwithonedimensionset',asyncfunction(assert){
        assert.expect(6);

        this.data.partner.fields.tortue={string:"Tortue",type:"char",default:"a"};

        constform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                '<fieldname="foo"widget="image_url"options="{\'size\':[180,0]}"/>'+
                '<fieldname="tortue"widget="image_url"options="{\'size\':[0,270]}"/>'+
                '</form>',
            res_id:6,
        });

        assert.containsOnce(form,'div[name="foo"]>img',"thewidgetshouldcontainanimage");
        assert.hasAttrValue(form.$('div[name="foo"]>img'),'width',"180",
            "theimageshouldcorrectlysetitsattributes");
        constimage1Style=form.$('div[name="foo"]>img').attr('style');
        assert.ok(['max-width:180px','height:auto','max-height:100%'].every(e=>image1Style.includes(e)),
            "theimageshouldcorrectlysetitsstyle");

        assert.containsOnce(form,'div[name="tortue"]>img',"thewidgetshouldcontainanimage");
        assert.hasAttrValue(form.$('div[name="tortue"]>img'),'height',"270",
            "theimageshouldcorrectlysetitsattributes");
        constimage2Style=form.$('div[name="tortue"]>img').attr('style');
        assert.ok(['max-height:270px','width:auto','max-width:100%'].every(e=>image2Style.includes(e)),
            "theimageshouldcorrectlysetitsstyle");

        form.destroy();
    });

    QUnit.test('image_urlwidgetinsubviewsareloadedcorrectly',asyncfunction(assert){
        assert.expect(6);

        this.data.partner_type.fields.image={name:'image',type:'char'};
        this.data.partner_type.records[0].image=EN_FLAG_URL;
        this.data.partner.records[5].timmy=[12];

        constform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<fieldname="foo"widget="image_url"options="{\'size\':[90,90]}"/>'+
                    '<fieldname="timmy"widget="many2many">'+
                        '<tree>'+
                            '<fieldname="display_name"/>'+
                        '</tree>'+
                        '<form>'+
                            '<fieldname="image"widget="image_url"/>'+
                        '</form>'+
                    '</field>'+
                '</form>',
            res_id:6,
            asyncmockRPC(route){
                if(route===FR_FLAG_URL){
                    assert.step("Theview'simageshouldhavebeenfetched");
                    return'wow';
                }
                if(route===EN_FLAG_URL){
                    assert.step("Thedialog'simageshouldhavebeenfetched");
                    return;
                }
                returnthis._super.apply(this,arguments);
            },
        });
        assert.verifySteps(["Theview'simageshouldhavebeenfetched"]);

        assert.containsOnce(form,'tr.o_data_row',
            'Thereshouldbeonerecordinthemany2many');

        //Actualflow:clickonanelementofthem2mtogetitsformview
        awaittestUtils.dom.click(form.$('tbodytd:contains(gold)'));
        assert.strictEqual($('.modal').length,1,
            'Themodalshouldhaveopened');
        assert.verifySteps(["Thedialog'simageshouldhavebeenfetched"]);

        form.destroy();
    });

    QUnit.test('imagefieldsinx2manylistareloadedcorrectly',asyncfunction(assert){
        assert.expect(2);

        this.data.partner_type.fields.image={name:'image',type:'char'};
        this.data.partner_type.records[0].image=EN_FLAG_URL;
        this.data.partner.records[5].timmy=[12];

        constform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<fieldname="timmy"widget="many2many">'+
                        '<tree>'+
                            '<fieldname="image"widget="image_url"/>'+
                        '</tree>'+
                    '</field>'+
                '</form>',
            res_id:6,
            asyncmockRPC(route){
                if(route===EN_FLAG_URL){
                    assert.ok(true,"Thelist'simageshouldhavebeenfetched");
                    return;
                }
                returnthis._super.apply(this,arguments);
            },
        });

        assert.containsOnce(form,'tr.o_data_row',
            'Thereshouldbeonerecordinthemany2many');

        form.destroy();
    });

    QUnit.module('JournalDashboardGraph',{
        beforeEach:function(){
            _.extend(this.data.partner.fields,{
                graph_data:{string:"GraphData",type:"text"},
                graph_type:{
                    string:"GraphType",
                    type:"selection",
                    selection:[['line','Line'],['bar','Bar']]
                },
            });
            this.data.partner.records[0].graph_type="bar";
            this.data.partner.records[1].graph_type="line";
            vargraph_values=[
                {'value':300,'label':'5-11Dec'},
                {'value':500,'label':'12-18Dec'},
                {'value':100,'label':'19-25Dec'},
            ];
            this.data.partner.records[0].graph_data=JSON.stringify([{
                color:'red',
                title:'Partner0',
                values:graph_values,
                key:'Akey',
                area:true,
            }]);
            this.data.partner.records[1].graph_data=JSON.stringify([{
                color:'blue',
                title:'Partner1',
                values:graph_values,
                key:'Akey',
                area:true,
            }]);
        },
    });

    QUnit.test('graphdashboardwidgetattach/detachcallbacks',asyncfunction(assert){
        //ThiswidgetisrenderedwithChart.js.
        vardone=assert.async();
        assert.expect(6);

        testUtils.mock.patch(JournalDashboardGraph,{
            on_attach_callback:function(){
                assert.step('on_attach_callback');
            },
            on_detach_callback:function(){
                assert.step('on_detach_callback');
            },
        });

        createView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:'<kanbanclass="o_kanban_test">'+
                    '<fieldname="graph_type"/>'+
                    '<templates><tt-name="kanban-box">'+
                        '<div>'+
                        '<fieldname="graph_data"t-att-graph_type="record.graph_type.raw_value"widget="dashboard_graph"/>'+
                        '</div>'+
                    '</t>'+
                '</templates></kanban>',
            domain:[['id','in',[1,2]]],
        }).then(function(kanban){
            assert.verifySteps([
                'on_attach_callback',
                'on_attach_callback'
            ]);

            kanban.on_detach_callback();

            assert.verifySteps([
                'on_detach_callback',
                'on_detach_callback'
            ]);

            kanban.destroy();
            testUtils.mock.unpatch(JournalDashboardGraph);
            done();
        });
    });

    QUnit.test('graphdashboardwidgetisrenderedcorrectly',asyncfunction(assert){
        vardone=assert.async();
        assert.expect(3);

        createView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:'<kanbanclass="o_kanban_test">'+
                    '<fieldname="graph_type"/>'+
                    '<templates><tt-name="kanban-box">'+
                        '<div>'+
                        '<fieldname="graph_data"t-att-graph_type="record.graph_type.raw_value"widget="dashboard_graph"/>'+
                        '</div>'+
                    '</t>'+
                '</templates></kanban>',
            domain:[['id','in',[1,2]]],
        }).then(function(kanban){
            concurrency.delay(0).then(function(){
                assert.strictEqual(kanban.$('.o_kanban_record:first().o_graph_barchart').length,1,
                    "graphoffirstrecordshouldbeabarchart");
                assert.strictEqual(kanban.$('.o_kanban_record:nth(1).o_dashboard_graph').length,1,
                    "graphofsecondrecordshouldbealinechart");

                //forceare-renderingofthefirstrecord(tocheckifthe
                //previousrenderedgraphiscorrectlyremovedfromtheDOM)
                varfirstRecordState=kanban.model.get(kanban.handle).data[0];
                returnkanban.renderer.updateRecord(firstRecordState);
            }).then(function(){
                returnconcurrency.delay(0);
            }).then(function(){
                assert.strictEqual(kanban.$('.o_kanban_record:first()canvas').length,1,
                    "thereshouldbeonlyonerenderedgraphbyrecord");

                kanban.destroy();
                done();
            });
        });
    });

    QUnit.test('renderingofafieldwithdashboard_graphwidgetinanupdatedkanbanview(ungrouped)',asyncfunction(assert){

        vardone=assert.async();
        assert.expect(2);

        createView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:'<kanbanclass="o_kanban_test">'+
                    '<fieldname="graph_type"/>'+
                    '<templates><tt-name="kanban-box">'+
                        '<div>'+
                        '<fieldname="graph_data"t-att-graph_type="record.graph_type.raw_value"widget="dashboard_graph"/>'+
                        '</div>'+
                    '</t>'+
                '</templates></kanban>',
            domain:[['id','in',[1,2]]],
        }).then(function(kanban){
            concurrency.delay(0).then(function(){
                assert.containsN(kanban,'.o_dashboard_graphcanvas',2,"thereshouldbetwographrendered");
                returnkanban.update({});
            }).then(function(){
                returnconcurrency.delay(0);//onegraphisre-rendered
            }).then(function(){
                assert.containsN(kanban,'.o_dashboard_graphcanvas',2,"thereshouldbeonegraphrendered");
                kanban.destroy();
                done();
            });
        });
    });

    QUnit.test('renderingofafieldwithdashboard_graphwidgetinanupdatedkanbanview(grouped)',asyncfunction(assert){

        vardone=assert.async();
        assert.expect(2);

        createView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:'<kanbanclass="o_kanban_test">'+
                    '<fieldname="graph_type"/>'+
                    '<templates><tt-name="kanban-box">'+
                        '<div>'+
                        '<fieldname="graph_data"t-att-graph_type="record.graph_type.raw_value"widget="dashboard_graph"/>'+
                        '</div>'+
                    '</t>'+
                '</templates></kanban>',
            domain:[['id','in',[1,2]]],
        }).then(function(kanban){
            concurrency.delay(0).then(function(){
                assert.containsN(kanban,'.o_dashboard_graphcanvas',2,"thereshouldbetwographrendered");
                returnkanban.update({groupBy:['selection'],domain:[['int_field','=',10]]});
            }).then(function(){
                assert.containsOnce(kanban,'.o_dashboard_graphcanvas',"thereshouldbeonegraphrendered");
                kanban.destroy();
                done();
            });
        });
    });

    QUnit.module('AceEditor');

    QUnit.test('acewidgetontextfieldsworks',asyncfunction(assert){
        assert.expect(2);
        vardone=assert.async();

        this.data.partner.fields.foo.type='text';
        testUtils.createView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<fieldname="foo"widget="ace"/>'+
                '</form>',
            res_id:1,
        }).then(function(form){
            assert.ok('ace'inwindow,"theacelibraryshouldbeloaded");
            assert.ok(form.$('div.ace_content').length,"shouldhaverenderedsomethingwithaceeditor");
            form.destroy();
            done();
        });
    });

    QUnit.module('HandleWidget');

    QUnit.test('handlewidgetinx2m',asyncfunction(assert){
        assert.expect(6);

        this.data.partner.records[0].p=[2,4];
        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                        '<fieldname="p">'+
                            '<treeeditable="bottom">'+
                                '<fieldname="sequence"widget="handle"/>'+
                                '<fieldname="display_name"/>'+
                            '</tree>'+
                        '</field>'+
                '</form>',
            res_id:1,
        });

        assert.strictEqual(form.$('tdspan.o_row_handle').text(),"",
            "handleshouldnothaveanycontent");

        assert.notOk(form.$('tdspan.o_row_handle').is(':visible'),
            "handleshouldbeinvisibleinreadonlymode");

        assert.containsN(form,'span.o_row_handle',2,"shouldhave2handles");

        awaittestUtils.form.clickEdit(form);

        assert.hasClass(form.$('td:first'),'o_handle_cell',
            "columnwidgetshouldbedisplayedincssclass");

        assert.ok(form.$('tdspan.o_row_handle').is(':visible'),
            "handleshouldbevisibleinreadonlymode");

        testUtils.dom.click(form.$('td').eq(1));
        assert.containsOnce(form,'td:firstspan.o_row_handle',
            "contentofthecellshouldhavebeenreplaced");
        form.destroy();
    });

    QUnit.test('handlewidgetwithfalsyvalues',asyncfunction(assert){
        assert.expect(1);

        varlist=awaitcreateView({
            View:ListView,
            model:'partner',
            data:this.data,
            arch:'<tree>'+
                    '<fieldname="sequence"widget="handle"/>'+
                    '<fieldname="display_name"/>'+
                '</tree>',
        });

        assert.containsN(list,'.o_row_handle:visible',this.data.partner.records.length,
            'thereshouldbeavisiblehandleforeachrecord');
        list.destroy();
    });


    QUnit.module('FieldDateRange');

    QUnit.test('Datetimefield[REQUIREFOCUS]',asyncfunction(assert){
        assert.expect(22);

        this.data.partner.fields.datetime_end={string:'DatetimeEnd',type:'datetime'};
        this.data.partner.records[0].datetime_end='2017-03-1300:00:00';

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<form>'+
                    '<fieldname="datetime"widget="daterange"options="{\'related_end_date\':\'datetime_end\'}"/>'+
                    '<fieldname="datetime_end"widget="daterange"options="{\'related_start_date\':\'datetime\'}"/>'+
                '</form>',
            res_id:1,
            session:{
                getTZOffset:function(){
                    return330;
                },
            },
        });

        //Checkdatedisplaycorrectlyinreadonly
        assert.strictEqual(form.$('.o_field_date_range:first').text(),'02/08/201715:30:00',
            "thestartdateshouldbecorrectlydisplayedinreadonly");
        assert.strictEqual(form.$('.o_field_date_range:last').text(),'03/13/201705:30:00',
            "theenddateshouldbecorrectlydisplayedinreadonly");

        //Edit
        awaittestUtils.form.clickEdit(form);

        //Checkdaterangepickerinitialization
        assert.containsN(document.body,'.daterangepicker',2,
            "shouldinitialize2daterangepicker");
        assert.strictEqual($('.daterangepicker:first').css('display'),'block',
            "daterangepickershouldbeopenedinitially");
        assert.strictEqual($('.daterangepicker:last').css('display'),'none',
            "daterangepickershouldbeclosedinitially");
        assert.strictEqual($('.daterangepicker:first.drp-calendar.left.active.start-date').text(),'8',
            "activestartdateshouldbe'8'indaterangepicker");
        assert.strictEqual($('.daterangepicker:first.drp-calendar.left.hourselect').val(),'15',
            "activestartdatehourshouldbe'15'indaterangepicker");
        assert.strictEqual($('.daterangepicker:first.drp-calendar.left.minuteselect').val(),'30',
            "activestartdateminuteshouldbe'30'indaterangepicker");
        assert.strictEqual($('.daterangepicker:first.drp-calendar.right.active.end-date').text(),'13',
            "activeenddateshouldbe'13'indaterangepicker");
        assert.strictEqual($('.daterangepicker:first.drp-calendar.right.hourselect').val(),'5',
            "activeenddatehourshouldbe'5'indaterangepicker");
        assert.strictEqual($('.daterangepicker:first.drp-calendar.right.minuteselect').val(),'30',
            "activeenddateminuteshouldbe'30'indaterangepicker");
        assert.containsN($('.daterangepicker:first.drp-calendar.left.minuteselect'),'option',12,
            "minuteselectionshouldcontain12options(1foreach5minutes)");

        //Closepicker
        awaittestUtils.dom.click($('.daterangepicker:first.cancelBtn'));
        assert.strictEqual($('.daterangepicker:first').css('display'),'none',
            "daterangepickershouldbeclosed");

        //Discardform,fieldsshouldn'tbealtered
        awaittestUtils.form.clickDiscard(form);
        assert.strictEqual(form.$('.o_field_date_range:first').text(),'02/08/201715:30:00',
            "thestartdateshouldbethesameasbeforeediting");
        assert.strictEqual(form.$('.o_field_date_range:last').text(),'03/13/201705:30:00',
            "theenddateshouldbethesameasbeforeediting");

        //Edit
        awaittestUtils.form.clickEdit(form);

        //Trytocheckwithenddate
        awaittestUtils.dom.click(form.$('.o_field_date_range:last'));
        assert.strictEqual($('.daterangepicker:last').css('display'),'block',
            "daterangepickershouldbeopened");
        assert.strictEqual($('.daterangepicker:last.drp-calendar.left.active.start-date').text(),'8',
            "activestartdateshouldbe'8'indaterangepicker");
        assert.strictEqual($('.daterangepicker:last.drp-calendar.left.hourselect').val(),'15',
            "activestartdatehourshouldbe'15'indaterangepicker");
        assert.strictEqual($('.daterangepicker:last.drp-calendar.left.minuteselect').val(),'30',
            "activestartdateminuteshouldbe'30'indaterangepicker");
        assert.strictEqual($('.daterangepicker:last.drp-calendar.right.active.end-date').text(),'13',
            "activeenddateshouldbe'13'indaterangepicker");
        assert.strictEqual($('.daterangepicker:last.drp-calendar.right.hourselect').val(),'5',
            "activeenddatehourshouldbe'5'indaterangepicker");
        assert.strictEqual($('.daterangepicker:last.drp-calendar.right.minuteselect').val(),'30',
            "activeenddateminuteshouldbe'30'indaterangepicker");

        form.destroy();
    });

    QUnit.test('Datefield[REQUIREFOCUS]',asyncfunction(assert){
        assert.expect(18);

        this.data.partner.fields.date_end={string:'DateEnd',type:'date'};
        this.data.partner.records[0].date_end='2017-02-08';

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<form>'+
                    '<fieldname="date"widget="daterange"options="{\'related_end_date\':\'date_end\'}"/>'+
                    '<fieldname="date_end"widget="daterange"options="{\'related_start_date\':\'date\'}"/>'+
                '</form>',
            res_id:1,
            session:{
                getTZOffset:function(){
                    return330;
                },
            },
        });

        //Checkdatedisplaycorrectlyinreadonly
        assert.strictEqual(form.$('.o_field_date_range:first').text(),'02/03/2017',
            "thestartdateshouldbecorrectlydisplayedinreadonly");
        assert.strictEqual(form.$('.o_field_date_range:last').text(),'02/08/2017',
            "theenddateshouldbecorrectlydisplayedinreadonly");

        //Edit
        awaittestUtils.form.clickEdit(form);

        //Checkdaterangepickerinitialization
        assert.containsN(document.body,'.daterangepicker',2,
            "shouldinitialize2daterangepicker");
        assert.strictEqual($('.daterangepicker:first').css('display'),'block',
            "daterangepickershouldbeopenedinitially");
        assert.strictEqual($('.daterangepicker:last').css('display'),'none',
            "daterangepickershouldbeclosedinitially");
        assert.strictEqual($('.daterangepicker:first.active.start-date').text(),'3',
            "activestartdateshouldbe'3'indaterangepicker");
        assert.strictEqual($('.daterangepicker:first.active.end-date').text(),'8',
            "activeenddateshouldbe'8'indaterangepicker");

        //Changedate
        awaittestUtils.dom.triggerMouseEvent($('.daterangepicker:first.drp-calendar.left.available:contains("16")'),'mousedown');
        awaittestUtils.dom.triggerMouseEvent($('.daterangepicker:first.drp-calendar.right.available:contains("12")'),'mousedown');
        awaittestUtils.dom.click($('.daterangepicker:first.applyBtn'));

        //Checkdateafterchange
        assert.strictEqual($('.daterangepicker:first').css('display'),'none',
            "daterangepickershouldbeclosed");
        assert.strictEqual(form.$('.o_field_date_range:first').val(),'02/16/2017',
            "thedateshouldbe'02/16/2017'");
        assert.strictEqual(form.$('.o_field_date_range:last').val(),'03/12/2017',
            "'thedateshouldbe'03/12/2017'");

        //Trytochangerangewithenddate
        awaittestUtils.dom.click(form.$('.o_field_date_range:last'));
        assert.strictEqual($('.daterangepicker:last').css('display'),'block',
            "daterangepickershouldbeopened");
        assert.strictEqual($('.daterangepicker:last.active.start-date').text(),'16',
            "startdateshouldbea16indaterangepicker");
        assert.strictEqual($('.daterangepicker:last.active.end-date').text(),'12',
            "enddateshouldbea12indaterangepicker");

        //Changedate
        awaittestUtils.dom.triggerMouseEvent($('.daterangepicker:last.drp-calendar.left.available:contains("13")'),'mousedown');
        awaittestUtils.dom.triggerMouseEvent($('.daterangepicker:last.drp-calendar.right.available:contains("18")'),'mousedown');
        awaittestUtils.dom.click($('.daterangepicker:last.applyBtn'));

        //Checkdateafterchange
        assert.strictEqual($('.daterangepicker:last').css('display'),'none',
            "daterangepickershouldbeclosed");
        assert.strictEqual(form.$('.o_field_date_range:first').val(),'02/13/2017',
            "thestartdateshouldbe'02/13/2017'");
        assert.strictEqual(form.$('.o_field_date_range:last').val(),'03/18/2017',
            "theenddateshouldbe'03/18/2017'");

        //Save
        awaittestUtils.form.clickSave(form);

        //Checkdateaftersave
        assert.strictEqual(form.$('.o_field_date_range:first').text(),'02/13/2017',
            "thestartdateshouldbe'02/13/2017'aftersave");
        assert.strictEqual(form.$('.o_field_date_range:last').text(),'03/18/2017',
            "theenddateshouldbe'03/18/2017'aftersave");

        form.destroy();
    });

    QUnit.test('daterangepickershoulddisappearonscrollingoutsideofit',asyncfunction(assert){
        assert.expect(2);

        this.data.partner.fields.datetime_end={string:'DatetimeEnd',type:'datetime'};
        this.data.partner.records[0].datetime_end='2017-03-1300:00:00';

        constform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:`
                <form>
                    <fieldname="datetime"widget="daterange"options="{'related_end_date':'datetime_end'}"/>
                    <fieldname="datetime_end"widget="daterange"options="{'related_start_date':'datetime'}"/>
                </form>`,
            res_id:1,
        });

        awaittestUtils.form.clickEdit(form);
        awaittestUtils.dom.click(form.$('.o_field_date_range:first'));

        assert.isVisible($('.daterangepicker:first'),"daterangepickershouldbeopened");

        form.el.dispatchEvent(newEvent('scroll'));
        assert.isNotVisible($('.daterangepicker:first'),"daterangepickershouldbeclosed");

        form.destroy();
    });

    QUnit.test('Datetimefieldmanuallyinputvalueshouldsendutcvaluetoserver',asyncfunction(assert){
        assert.expect(4);

        this.data.partner.fields.datetime_end={string:'DatetimeEnd',type:'datetime'};
        this.data.partner.records[0].datetime_end='2017-03-1300:00:00';

        constform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:`
                <form>
                    <fieldname="datetime"widget="daterange"options="{'related_end_date':'datetime_end'}"/>
                    <fieldname="datetime_end"widget="daterange"options="{'related_start_date':'datetime'}"/>
                </form>`,
            res_id:1,
            session:{
                getTZOffset:function(){
                    return330;
                },
            },
            mockRPC:function(route,args){
                if(args.method==='write'){
                    assert.deepEqual(args.args[1],{datetime:'2017-02-0806:00:00'});
                }
                returnthis._super(...arguments);
            },
        });

        //checkdatedisplaycorrectlyinreadonly
        assert.strictEqual(form.$('.o_field_date_range:first').text(),'02/08/201715:30:00',
            "thestartdateshouldbecorrectlydisplayedinreadonly");
        assert.strictEqual(form.$('.o_field_date_range:last').text(),'03/13/201705:30:00',
            "theenddateshouldbecorrectlydisplayedinreadonly");

        //editform
        awaittestUtils.form.clickEdit(form);
        //updateinputforDatetime
        awaittestUtils.fields.editInput(form.$('.o_field_date_range:first'),'02/08/201711:30:00');
        //saveform
        awaittestUtils.form.clickSave(form);

        assert.strictEqual(form.$('.o_field_date_range:first').text(),'02/08/201711:30:00',
            "thestartdateshouldbecorrectlydisplayedinreadonlyaftermanualupdate");

        form.destroy();
    });

    QUnit.test('Daterangefieldmanuallyinputwrongvalueshouldshowtoaster',asyncfunction(assert){
        assert.expect(5);

        this.data.partner.fields.date_end={string:'DateEnd',type:'date'};
        this.data.partner.records[0].date_end='2017-02-08';

        constform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:`
            <form>
                <fieldname="date"widget="daterange"options="{'related_end_date':'date_end'}"/>
                <fieldname="date_end"widget="daterange"options="{'related_start_date':'date'}"/>
            </form>`,
            interceptsPropagate:{
                call_service:function(ev){
                    if(ev.data.service==='notification'){
                        assert.strictEqual(ev.data.method,'notify');
                        assert.strictEqual(ev.data.args[0].title,'Invalidfields:');
                        assert.strictEqual(ev.data.args[0].message,'<ul><li>Adate</li></ul>');
                    }
                }
            },
        });

        awaittestUtils.fields.editInput(form.$('.o_field_date_range:first'),'blabla');
        //clickoutsidedaterangefield
        awaittestUtils.dom.click(form.$el);
        assert.hasClass(form.$('input[name=date]'),'o_field_invalid',
            "datefieldshouldbedisplayedasinvalid");
        //updateinputdatewithrightvalue
        awaittestUtils.fields.editInput(form.$('.o_field_date_range:first'),'02/08/2017');
        assert.doesNotHaveClass(form.$('input[name=date]'),'o_field_invalid',
            "datefieldshouldnotbedisplayedasinvalidnow");

        //againenterwrongvalueandtrytosaveshouldraiseinvalidfieldsvalue
        awaittestUtils.fields.editInput(form.$('.o_field_date_range:first'),'blabla');
        awaittestUtils.form.clickSave(form);

        form.destroy();
    });

    QUnit.module('FieldDate');

    QUnit.test('datefield:toggledatepicker[REQUIREFOCUS]',asyncfunction(assert){
        assert.expect(3);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<form><fieldname="foo"/><fieldname="date"/></form>',
            translateParameters:{ //Avoidissuesduetolocalizationformats
                date_format:'%m/%d/%Y',
            },
        });

        assert.strictEqual($('.bootstrap-datetimepicker-widget:visible').length,0,
            "datepickershouldbeclosedinitially");

        awaittestUtils.dom.openDatepicker(form.$('.o_datepicker'));

        assert.strictEqual($('.bootstrap-datetimepicker-widget:visible').length,1,
            "datepickershouldbeopened");

        //focusanotherfield
        awaittestUtils.dom.click(form.$('.o_field_widget[name=foo]').focus().mouseenter());

        assert.strictEqual($('.bootstrap-datetimepicker-widget:visible').length,0,
            "datepickershouldcloseitselfwhentheuserclicksoutside");

        form.destroy();
    });

    QUnit.test('datefield:toggledatepickerfarinthefuture',asyncfunction(assert){
        assert.expect(3);

        this.data.partner.records=[{
            id:1,
            date:"9999-12-30",
            foo:"yop",
        }]

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<form><fieldname="foo"/><fieldname="date"/></form>',
            translateParameters:{ //Avoidissuesduetolocalizationformats
                date_format:'%m/%d/%Y',
            },
            res_id:1,
            viewOptions:{
                mode:'edit',
            },
        });

        assert.strictEqual($('.bootstrap-datetimepicker-widget:visible').length,0,
            "datepickershouldbeclosedinitially");

        testUtils.openDatepicker(form.$('.o_datepicker'));

        assert.strictEqual($('.bootstrap-datetimepicker-widget:visible').length,1,
            "datepickershouldbeopened");

        //focusanotherfield
        form.$('.o_field_widget[name=foo]').click().focus();

        assert.strictEqual($('.bootstrap-datetimepicker-widget:visible').length,0,
            "datepickershouldcloseitselfwhentheuserclicksoutside");

        form.destroy();
    });

    QUnit.test('datefieldisemptyifnodateisset',asyncfunction(assert){
        assert.expect(2);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners"><fieldname="date"/></form>',
            res_id:4,
        });
        var$span=form.$('span.o_field_widget');
        assert.strictEqual($span.length,1,"shouldhaveonespanintheformview");
        assert.strictEqual($span.text(),"","anditshouldbeempty");
        form.destroy();
    });

    QUnit.test('datefield:setaninvaliddatewhenthefieldisalreadyset',asyncfunction(assert){
        assert.expect(2);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners"><fieldname="date"/></form>',
            res_id:1,
            viewOptions:{
                mode:'edit',
            },
        });

        var$input=form.$('.o_field_widget[name=date]input');

        assert.strictEqual($input.val(),"02/03/2017");

        $input.val('mmmh').trigger('change');
        assert.strictEqual($input.val(),"02/03/2017","shouldhaveresettheoriginalvalue");

        form.destroy();
    });

    QUnit.test('datefield:setaninvaliddatewhenthefieldisnotsetyet',asyncfunction(assert){
        assert.expect(2);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners"><fieldname="date"/></form>',
            res_id:4,
            viewOptions:{
                mode:'edit',
            },
        });

        var$input=form.$('.o_field_widget[name=date]input');

        assert.strictEqual($input.text(),"");

        $input.val('mmmh').trigger('change');
        assert.strictEqual($input.text(),"","Thedatefieldshouldbeempty");

        form.destroy();
    });

    QUnit.test('datefieldvalueshouldnotsetonfirstclick',asyncfunction(assert){
        assert.expect(2);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners"><fieldname="date"/></form>',
            res_id:4,
        });

        awaittestUtils.form.clickEdit(form);

        //opendatepickerandselectadate
        testUtils.dom.openDatepicker(form.$('.o_datepicker'));
        assert.strictEqual(form.$('.o_datepicker_input').val(),'',"datefield'sinputshouldbeemptyonfirstclick");
        testUtils.dom.click($('.day:contains(22)'));

        //re-opendatepicker
        testUtils.dom.openDatepicker(form.$('.o_datepicker'));
        assert.strictEqual($('.day.active').text(),'22',
            "datepickershouldbehighlightwith22nddayofmonth");

        form.destroy();
    });

    QUnit.test('datefieldinformview(withpositivetimezoneoffset)',asyncfunction(assert){
        assert.expect(8);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners"><fieldname="date"/></form>',
            res_id:1,
            mockRPC:function(route,args){
                if(route==='/web/dataset/call_kw/partner/write'){
                    assert.strictEqual(args.args[1].date,'2017-02-22','thecorrectvalueshouldbesaved');
                }
                returnthis._super.apply(this,arguments);
            },
            translateParameters:{ //Avoidissuesduetolocalizationformats
              date_format:'%m/%d/%Y',
            },
            session:{
                getTZOffset:function(){
                    return120;//Shouldbeignoredbydatefields
                },
            },
        });

        assert.strictEqual(form.$('.o_field_date').text(),'02/03/2017',
            'thedateshouldbecorrectlydisplayedinreadonly');

        //switchtoeditmode
        awaittestUtils.form.clickEdit(form);
        assert.strictEqual(form.$('.o_datepicker_input').val(),'02/03/2017',
            'thedateshouldbecorrectineditmode');

        //opendatepickerandselectanothervalue
        testUtils.dom.openDatepicker(form.$('.o_datepicker'));
        assert.ok($('.bootstrap-datetimepicker-widget').length,'datepickershouldbeopen');
        assert.strictEqual($('.day.active').data('day'),'02/03/2017','datepickershouldbehighlightFebruary3');
        testUtils.dom.click($('.bootstrap-datetimepicker-widget.picker-switch').first());
        testUtils.dom.click($('.bootstrap-datetimepicker-widget.picker-switch:eq(1)').first());
        testUtils.dom.click($('.bootstrap-datetimepicker-widget.year:contains(2017)'));
        testUtils.dom.click($('.bootstrap-datetimepicker-widget.month').eq(1));
        testUtils.dom.click($('.day:contains(22)'));
        assert.ok(!$('.bootstrap-datetimepicker-widget').length,'datepickershouldbeclosed');
        assert.strictEqual(form.$('.o_datepicker_input').val(),'02/22/2017',
            'theselecteddateshouldbedisplayedintheinput');

        //save
        awaittestUtils.form.clickSave(form);
        assert.strictEqual(form.$('.o_field_date').text(),'02/22/2017',
            'theselecteddateshouldbedisplayedaftersaving');
        form.destroy();
    });

    QUnit.test('datefieldinformview(withnegativetimezoneoffset)',asyncfunction(assert){
        assert.expect(2);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners"><fieldname="date"/></form>',
            res_id:1,
            translateParameters:{ //Avoidissuesduetolocalizationformats
              date_format:'%m/%d/%Y',
            },
            session:{
                getTZOffset:function(){
                    return-120;//Shouldbeignoredbydatefields
                },
            },
        });

        assert.strictEqual(form.$('.o_field_date').text(),'02/03/2017',
            'thedateshouldbecorrectlydisplayedinreadonly');

        //switchtoeditmode
        awaittestUtils.form.clickEdit(form);
        assert.strictEqual(form.$('.o_datepicker_input').val(),'02/03/2017',
            'thedateshouldbecorrectineditmode');

        form.destroy();
    });

    QUnit.test('datefielddropdowndisappearsonscroll',asyncfunction(assert){
        assert.expect(2);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:
                '<form>'+
                    '<divclass="scrollable"style="height:2000px;">'+
                        '<fieldname="date"/>'+
                    '</div>'+
                '</form>',
            res_id:1,
        });

        awaittestUtils.form.clickEdit(form);
        awaittestUtils.dom.openDatepicker(form.$('.o_datepicker'));

        assert.containsOnce($('body'),'.bootstrap-datetimepicker-widget',"datepickershouldbeopened");

        form.el.dispatchEvent(newEvent('wheel'));
        assert.containsNone($('body'),'.bootstrap-datetimepicker-widget',"datepickershouldbeclosed");

        form.destroy();
    });

    QUnit.test('datefieldwithwarn_futureoption',asyncfunction(assert){
        assert.expect(2);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<fieldname="date"options="{\'datepicker\':{\'warn_future\':true}}"/>'+
                 '</form>',
            res_id:4,
        });

        //switchtoeditmode
        awaittestUtils.form.clickEdit(form);
        //opendatepickerandselectanothervalue
        awaittestUtils.dom.openDatepicker(form.$('.o_datepicker'));
        awaittestUtils.dom.click($('.bootstrap-datetimepicker-widget.picker-switch').first());
        awaittestUtils.dom.click($('.bootstrap-datetimepicker-widget.picker-switch:eq(1)'));
        awaittestUtils.dom.click($('.bootstrap-datetimepicker-widget.year').eq(11));
        awaittestUtils.dom.click($('.bootstrap-datetimepicker-widget.month').eq(11));
        awaittestUtils.dom.click($('.day:contains(31)'));

        var$warn=form.$('.o_datepicker_warning:visible');
        assert.strictEqual($warn.length,1,"shouldhaveawarningintheformview");

        awaittestUtils.fields.editSelect(form.$('.o_field_widget[name=date]input'),''); //removethevalue

        $warn=form.$('.o_datepicker_warning:visible');
        assert.strictEqual($warn.length,0,"thewarningintheformviewshouldbehidden");

        form.destroy();
    });

    QUnit.test('datefieldwithwarn_futureoption:donotoverwritedatepickeroption',asyncfunction(assert){
        assert.expect(2);

        //Makingsurewedon'thavealegitdefaultvalue
        //oranyonchangethatwouldsetthevalue
        this.data.partner.fields.date.default=undefined;
        this.data.partner.onchanges={};

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<fieldname="foo"/>'+//Donotletthedatefieldgetthefocusinthefirstplace
                    '<fieldname="date"options="{\'datepicker\':{\'warn_future\':true}}"/>'+
                 '</form>',
            res_id:1,
        });

        //switchtoeditmode
        awaittestUtils.form.clickEdit(form);
        assert.strictEqual(form.$('input[name="date"]').val(),'02/03/2017',
        'Theexistingrecordshouldhaveavalueforthedatefield');

        //savewithnochanges
        awaittestUtils.form.clickSave(form);

        //Createanewrecord
        awaittestUtils.form.clickCreate(form);

        assert.notOk(form.$('input[name="date"]').val(),
            'Thenewrecordshouldnothaveavaluethattheframeworkwouldhaveset');

        form.destroy();
    });

    QUnit.test('datefieldineditablelistview',asyncfunction(assert){
        assert.expect(8);

        varlist=awaitcreateView({
            View:ListView,
            model:'partner',
            data:this.data,
            arch:'<treeeditable="bottom">'+
                    '<fieldname="date"/>'+
                  '</tree>',
            translateParameters:{ //Avoidissuesduetolocalizationformats
                date_format:'%m/%d/%Y',
            },
            session:{
                getTZOffset:function(){
                    return0;
                },
            },
        });

        var$cell=list.$('tr.o_data_rowtd:not(.o_list_record_selector)').first();
        assert.strictEqual($cell.text(),'02/03/2017',
            'thedateshouldbedisplayedcorrectlyinreadonly');
        awaittestUtils.dom.click($cell);

        assert.containsOnce(list,'input.o_datepicker_input',
            "theviewshouldhaveadateinputforeditablemode");

        assert.strictEqual(list.$('input.o_datepicker_input').get(0),document.activeElement,
            "dateinputshouldhavethefocus");

        assert.strictEqual(list.$('input.o_datepicker_input').val(),'02/03/2017',
            'thedateshouldbecorrectineditmode');

        //opendatepickerandselectanothervalue
        awaittestUtils.dom.openDatepicker(list.$('.o_datepicker'));
        assert.ok($('.bootstrap-datetimepicker-widget').length,'datepickershouldbeopen');
        awaittestUtils.dom.click($('.bootstrap-datetimepicker-widget.picker-switch').first());
        awaittestUtils.dom.click($('.bootstrap-datetimepicker-widget.picker-switch:eq(1)'));
        awaittestUtils.dom.click($('.bootstrap-datetimepicker-widget.year:contains(2017)'));
        awaittestUtils.dom.click($('.bootstrap-datetimepicker-widget.month').eq(1));
        awaittestUtils.dom.click($('.day:contains(22)'));
        assert.ok(!$('.bootstrap-datetimepicker-widget').length,'datepickershouldbeclosed');
        assert.strictEqual(list.$('.o_datepicker_input').val(),'02/22/2017',
            'theselecteddateshouldbedisplayedintheinput');

        //save
        awaittestUtils.dom.click(list.$buttons.find('.o_list_button_save'));
        assert.strictEqual(list.$('tr.o_data_rowtd:not(.o_list_record_selector)').text(),'02/22/2017',
            'theselecteddateshouldbedisplayedaftersaving');

        list.destroy();
    });

    QUnit.test('datefieldremovevalue',asyncfunction(assert){
        assert.expect(4);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners"><fieldname="date"/></form>',
            res_id:1,
            mockRPC:function(route,args){
                if(route==='/web/dataset/call_kw/partner/write'){
                    assert.strictEqual(args.args[1].date,false,'thecorrectvalueshouldbesaved');
                }
                returnthis._super.apply(this,arguments);
            },
            translateParameters:{ //Avoidissuesduetolocalizationformats
                date_format:'%m/%d/%Y',
            },
        });

        //switchtoeditmode
        awaittestUtils.form.clickEdit(form);
        assert.strictEqual(form.$('.o_datepicker_input').val(),'02/03/2017',
            'thedateshouldbecorrectineditmode');

        awaittestUtils.fields.editAndTrigger(form.$('.o_datepicker_input'),'',['input','change','focusout']);
        assert.strictEqual(form.$('.o_datepicker_input').val(),'',
            'shouldhavecorrectlyremovedthevalue');

        //save
        awaittestUtils.form.clickSave(form);
        assert.strictEqual(form.$('.o_field_date').text(),'',
            'theselecteddateshouldbedisplayedaftersaving');

        form.destroy();
    });

    QUnit.test('donottriggerafield_changedfordatetimefieldwithdatewidget',asyncfunction(assert){
        assert.expect(3);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners"><fieldname="datetime"widget="date"/></form>',
            translateParameters:{ //Avoidissuesduetolocalizationformats
                date_format:'%m/%d/%Y',
                time_format:'%H:%M:%S',
            },
            res_id:1,
            viewOptions:{
                mode:'edit',
            },
            mockRPC:function(route,args){
                assert.step(args.method);
                returnthis._super.apply(this,arguments);
            },
        });

        assert.strictEqual(form.$('.o_datepicker_input').val(),'02/08/2017',
            'thedateshouldbecorrect');

        testUtils.fields.editAndTrigger(form.$('input[name="datetime"]'),'02/08/2017',['input','change','focusout']);
        awaittestUtils.form.clickSave(form);

        assert.verifySteps(['read']);//shouldnothavesaveasnothingchanged

        form.destroy();
    });

    QUnit.test('fielddateshouldselectitscontentonclickwhenthereisone',asyncfunction(assert){
        assert.expect(2);
        vardone=assert.async();

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<form><fieldname="date"/></form>',
            res_id:1,
            viewOptions:{
                mode:'edit',
            },
        });

        form.$el.on({
            'show.datetimepicker':function(){
                assert.ok($('.bootstrap-datetimepicker-widget').is(':visible'),
                    'bootstrap-datetimepickerisvisible');
                assert.strictEqual(window.getSelection().toString(),"02/03/2017",
                    'Thewholeinputofthedatefieldshouldhavebeenselected');
                done();
            }
        });

        testUtils.dom.openDatepicker(form.$('.o_datepicker'));

        form.destroy();
    });

    QUnit.test('datefieldsupportinternalization',asyncfunction(assert){
        assert.expect(2);

        varoriginalLocale=moment.locale();
        varoriginalParameters=_.clone(core._t.database.parameters);

        _.extend(core._t.database.parameters,{date_format:'%d.%b%Y',time_format:'%H:%M:%S'});
        moment.defineLocale('norvegianForTest',{
            monthsShort:'jan._feb._mars_april_mai_juni_juli_aug._sep._okt._nov._des.'.split('_'),
            monthsParseExact:true,
            dayOfMonthOrdinalParse:/\d{1,2}\./,
            ordinal:'%d.',
        });

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners"><fieldname="date"/></form>',
            res_id:1,
        });

        vardateViewForm=form.$('.o_field_date').text();
        awaittestUtils.dom.click(form.$buttons.find('.o_form_button_edit'));
        awaittestUtils.openDatepicker(form.$('.o_datepicker'));
        assert.strictEqual(form.$('.o_datepicker_input').val(),dateViewForm,
            "inputdatefieldshouldbethesameasitwasintheviewform");

        awaittestUtils.dom.click($('.day:contains(30)'));
        vardateEditForm=form.$('.o_datepicker_input').val();
        awaittestUtils.dom.click(form.$buttons.find('.o_form_button_save'));
        assert.strictEqual(form.$('.o_field_date').text(),dateEditForm,
            "datefieldshouldbethesameastheoneselectedintheviewform");

        moment.locale(originalLocale);
        moment.updateLocale('norvegianForTest',null);
        core._t.database.parameters=originalParameters;

        form.destroy();
    });

    QUnit.test('datefield:hitentershouldupdatevalue',asyncfunction(assert){
        assert.expect(2);

        constform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners"><fieldname="date"/></form>',
            res_id:1,
            translateParameters:{ //Avoidissuesduetolocalizationformats
                date_format:'%m/%d/%Y',
            },
            viewOptions:{
                mode:'edit',
            },
            session:{
                getTZOffset:function(){
                    return120;
                },
            },
        });

        constyear=(newDate()).getFullYear();

        awaittestUtils.fields.editInput(form.el.querySelector('input[name="date"]'),'01/08');
        awaittestUtils.fields.triggerKeydown(form.el.querySelector('input[name="date"]'),'enter');
        assert.strictEqual(form.el.querySelector('input[name="date"]').value,'01/08/'+year);

        awaittestUtils.fields.editInput(form.el.querySelector('input[name="date"]'),'08/01');
        awaittestUtils.fields.triggerKeydown(form.el.querySelector('input[name="date"]'),'enter');
        assert.strictEqual(form.el.querySelector('input[name="date"]').value,'08/01/'+year);

        form.destroy();
    });

    QUnit.test('focuseddatefieldshouldcausenoerrorondestroy',asyncfunction(assert){
        assert.expect(2);

        varoriginalParameters=_.clone(core._t.database.parameters);
        _.extend(core._t.database.parameters,{date_format:'%d.%m:%Y'});

        varlist=awaitcreateView({
            View:ListView,
            model:'partner',
            data:this.data,
            arch:'<treeeditable="top"><fieldname="date"/></tree>',
            domain:[(1,'=',0)],
            context:{'default_date':'2020-01-2000:00:00'},
        });

        awaittestUtils.dom.click(list.$('.o_list_button_add'));
        assert.containsOnce(list,'.o_data_row');
        awaittestUtils.fields.triggerKeydown($(document.activeElement),'escape');
        assert.containsNone(list,'.o_data_row');

        list.destroy();
        core._t.database.parameters=originalParameters;
    });

    QUnit.module('FieldDatetime');

    QUnit.test('datetimefieldinformview',asyncfunction(assert){
        assert.expect(7);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners"><fieldname="datetime"/></form>',
            res_id:1,
            translateParameters:{ //Avoidissuesduetolocalizationformats
                date_format:'%m/%d/%Y',
                time_format:'%H:%M:%S',
            },
            session:{
                getTZOffset:function(){
                    return120;
                },
            },
        });

        varexpectedDateString="02/08/201712:00:00";//10:00:00withouttimezone
        assert.strictEqual(form.$('.o_field_date').text(),expectedDateString,
            'thedatetimeshouldbecorrectlydisplayedinreadonly');

        //switchtoeditmode
        awaittestUtils.form.clickEdit(form);
        assert.strictEqual(form.$('.o_datepicker_input').val(),expectedDateString,
            'thedatetimeshouldbecorrectineditmode');

        //datepickershouldnotopenonfocus
        assert.containsNone($('body'),'.bootstrap-datetimepicker-widget');

        testUtils.dom.openDatepicker(form.$('.o_datepicker'));
        assert.containsOnce($('body'),'.bootstrap-datetimepicker-widget');

        //select22Februaryat8:23:33
        awaittestUtils.dom.click($('.bootstrap-datetimepicker-widget.picker-switch').first());
        awaittestUtils.dom.click($('.bootstrap-datetimepicker-widget.picker-switch:eq(1)'));
        awaittestUtils.dom.click($('.bootstrap-datetimepicker-widget.year:contains(2017)'));
        awaittestUtils.dom.click($('.bootstrap-datetimepicker-widget.month').eq(3));
        awaittestUtils.dom.click($('.bootstrap-datetimepicker-widget.day:contains(22)'));
        awaittestUtils.dom.click($('.bootstrap-datetimepicker-widget.fa-clock-o'));
        awaittestUtils.dom.click($('.bootstrap-datetimepicker-widget.timepicker-hour'));
        awaittestUtils.dom.click($('.bootstrap-datetimepicker-widget.hour:contains(08)'));
        awaittestUtils.dom.click($('.bootstrap-datetimepicker-widget.timepicker-minute'));
        awaittestUtils.dom.click($('.bootstrap-datetimepicker-widget.minute:contains(25)'));
        awaittestUtils.dom.click($('.bootstrap-datetimepicker-widget.timepicker-second'));
        awaittestUtils.dom.click($('.bootstrap-datetimepicker-widget.second:contains(35)'));
        assert.ok(!$('.bootstrap-datetimepicker-widget').length,'datepickershouldbeclosed');

        varnewExpectedDateString="04/22/201708:25:35";
        assert.strictEqual(form.$('.o_datepicker_input').val(),newExpectedDateString,
            'theselecteddateshouldbedisplayedintheinput');

        //save
        awaittestUtils.form.clickSave(form);
        assert.strictEqual(form.$('.o_field_date').text(),newExpectedDateString,
            'theselecteddateshouldbedisplayedaftersaving');

        form.destroy();
    });

    QUnit.test('datetimefieldsdonottriggerfieldChangebeforedatetimecompletlypicked',asyncfunction(assert){
        assert.expect(6);

        this.data.partner.onchanges={
            datetime:function(){},
        };
        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<form><fieldname="datetime"/></form>',
            res_id:1,
            translateParameters:{//Avoidissuesduetolocalizationformats
                date_format:'%m/%d/%Y',
                time_format:'%H:%M:%S',
            },
            session:{
                getTZOffset:function(){
                    return120;
                },
            },
            mockRPC:function(route,args){
                if(args.method==='onchange'){
                    assert.step('onchange');
                }
                returnthis._super.apply(this,arguments);
            },
            viewOptions:{
                mode:'edit',
            },
        });


        testUtils.dom.openDatepicker(form.$('.o_datepicker'));
        assert.containsOnce($('body'),'.bootstrap-datetimepicker-widget');

        //selectadateandtime
        awaittestUtils.dom.click($('.bootstrap-datetimepicker-widget.picker-switch').first());
        awaittestUtils.dom.click($('.bootstrap-datetimepicker-widget.picker-switch:eq(1)'));
        awaittestUtils.dom.click($('.bootstrap-datetimepicker-widget.year:contains(2017)'));
        awaittestUtils.dom.click($('.bootstrap-datetimepicker-widget.month').eq(3));
        awaittestUtils.dom.click($('.bootstrap-datetimepicker-widget.day:contains(22)'));
        awaittestUtils.dom.click($('.bootstrap-datetimepicker-widget.fa-clock-o'));
        awaittestUtils.dom.click($('.bootstrap-datetimepicker-widget.timepicker-hour'));
        awaittestUtils.dom.click($('.bootstrap-datetimepicker-widget.hour:contains(08)'));
        awaittestUtils.dom.click($('.bootstrap-datetimepicker-widget.timepicker-minute'));
        awaittestUtils.dom.click($('.bootstrap-datetimepicker-widget.minute:contains(25)'));
        awaittestUtils.dom.click($('.bootstrap-datetimepicker-widget.timepicker-second'));
        assert.verifySteps([],"shouldnothavedoneanyonchangeyet");
        awaittestUtils.dom.click($('.bootstrap-datetimepicker-widget.second:contains(35)'));

        assert.containsNone($('body'),'.bootstrap-datetimepicker-widget');
        assert.strictEqual(form.$('.o_datepicker_input').val(),"04/22/201708:25:35");
        assert.verifySteps(['onchange'],"shouldhavedoneonlyoneonchange");

        form.destroy();
    });

    QUnit.test('datetimefieldnotvisibleinformviewshouldnotcapturethefocusonkeyboardnavigation',asyncfunction(assert){
        assert.expect(1);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners"><fieldname="txt"/>'+
            '<fieldname="datetime"invisible="True"/></form>',
            res_id:1,
            viewOptions:{
                mode:'edit',
            },
        });

        form.$el.find('textarea[name=txt]').trigger($.Event('keydown',{
            which:$.ui.keyCode.TAB,
            keyCode:$.ui.keyCode.TAB,
        }));
        assert.strictEqual(document.activeElement,form.$buttons.find('.o_form_button_save')[0],
            "thesavebuttonshouldbeselected,becausethedatepickerdidnotcapturethefocus");
        form.destroy();
    });

    QUnit.test('datetimefieldwithdatetimeformattedwithoutsecond',asyncfunction(assert){
        assert.expect(2);

        this.data.partner.fields.datetime.default="2017-08-0212:00:05";
        this.data.partner.fields.datetime.required=true;

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners"><fieldname="datetime"/></form>',
            translateParameters:{ //Avoidissuesduetolocalizationformats
                date_format:'%m/%d/%Y',
                time_format:'%H:%M',
            },
        });

        varexpectedDateString="08/02/201712:00";//10:00:00withouttimezone
        assert.strictEqual(form.$('.o_field_dateinput').val(),expectedDateString,
            'thedatetimeshouldbecorrectlydisplayedinreadonly');

        awaittestUtils.form.clickDiscard(form);

        assert.strictEqual($('.modal').length,0,
            "thereshouldnotbeaWarningdialog");

        form.destroy();
    });

    QUnit.test('datetimefieldineditablelistview',asyncfunction(assert){
        assert.expect(9);

        varlist=awaitcreateView({
            View:ListView,
            model:'partner',
            data:this.data,
            arch:'<treeeditable="bottom">'+
                    '<fieldname="datetime"/>'+
                  '</tree>',
            translateParameters:{ //Avoidissuesduetolocalizationformats
                date_format:'%m/%d/%Y',
                time_format:'%H:%M:%S',
            },
            session:{
                getTZOffset:function(){
                    return120;
                },
            },
        });

        varexpectedDateString="02/08/201712:00:00";//10:00:00withouttimezone
        var$cell=list.$('tr.o_data_rowtd:not(.o_list_record_selector)').first();
        assert.strictEqual($cell.text(),expectedDateString,
            'thedatetimeshouldbecorrectlydisplayedinreadonly');

        //switchtoeditmode
        awaittestUtils.dom.click($cell);
        assert.containsOnce(list,'input.o_datepicker_input',
            "theviewshouldhaveadateinputforeditablemode");

        assert.strictEqual(list.$('input.o_datepicker_input').get(0),document.activeElement,
            "dateinputshouldhavethefocus");

        assert.strictEqual(list.$('input.o_datepicker_input').val(),expectedDateString,
            'thedateshouldbecorrectineditmode');

        assert.containsNone($('body'),'.bootstrap-datetimepicker-widget');
        testUtils.dom.openDatepicker(list.$('.o_datepicker'));
        assert.containsOnce($('body'),'.bootstrap-datetimepicker-widget');

        //select22Februaryat8:23:33
        awaittestUtils.dom.click($('.bootstrap-datetimepicker-widget.picker-switch').first());
        awaittestUtils.dom.click($('.bootstrap-datetimepicker-widget.picker-switch:eq(1)'));
        awaittestUtils.dom.click($('.bootstrap-datetimepicker-widget.year:contains(2017)'));
        awaittestUtils.dom.click($('.bootstrap-datetimepicker-widget.month').eq(3));
        awaittestUtils.dom.click($('.bootstrap-datetimepicker-widget.day:contains(22)'));
        awaittestUtils.dom.click($('.bootstrap-datetimepicker-widget.fa-clock-o'));
        awaittestUtils.dom.click($('.bootstrap-datetimepicker-widget.timepicker-hour'));
        awaittestUtils.dom.click($('.bootstrap-datetimepicker-widget.hour:contains(08)'));
        awaittestUtils.dom.click($('.bootstrap-datetimepicker-widget.timepicker-minute'));
        awaittestUtils.dom.click($('.bootstrap-datetimepicker-widget.minute:contains(25)'));
        awaittestUtils.dom.click($('.bootstrap-datetimepicker-widget.timepicker-second'));
        awaittestUtils.dom.click($('.bootstrap-datetimepicker-widget.second:contains(35)'));
        assert.ok(!$('.bootstrap-datetimepicker-widget').length,'datepickershouldbeclosed');

        varnewExpectedDateString="04/22/201708:25:35";
        assert.strictEqual(list.$('.o_datepicker_input').val(),newExpectedDateString,
            'theselecteddatetimeshouldbedisplayedintheinput');

        //save
        awaittestUtils.dom.click(list.$buttons.find('.o_list_button_save'));
        assert.strictEqual(list.$('tr.o_data_rowtd:not(.o_list_record_selector)').text(),newExpectedDateString,
            'theselecteddatetimeshouldbedisplayedaftersaving');

        list.destroy();
    });

    QUnit.test('multieditionofdatetimefieldinlistview:editdateininput',asyncfunction(assert){
        assert.expect(4);

        varlist=awaitcreateView({
            View:ListView,
            model:'partner',
            data:this.data,
            arch:'<treemulti_edit="1">'+
                    '<fieldname="datetime"/>'+
                  '</tree>',
            translateParameters:{//Avoidissuesduetolocalizationformats
                date_format:'%m/%d/%Y',
                time_format:'%H:%M:%S',
            },
            session:{
                getTZOffset:function(){
                    return120;
                },
            },
        });

        //selecttworecordsandeditthem
        awaittestUtils.dom.click(list.$('.o_data_row:eq(0).o_list_record_selectorinput'));
        awaittestUtils.dom.click(list.$('.o_data_row:eq(1).o_list_record_selectorinput'));

        awaittestUtils.dom.click(list.$('.o_data_row:first.o_data_cell'));
        assert.containsOnce(list,'input.o_datepicker_input');
        list.$('.o_datepicker_input').val("10/02/201909:00:00");
        awaittestUtils.dom.triggerEvents(list.$('.o_datepicker_input'),['change']);

        assert.containsOnce(document.body,'.modal');
        awaittestUtils.dom.click($('.modal.modal-footer.btn-primary'));

        assert.strictEqual(list.$('.o_data_row:first.o_data_cell').text(),"10/02/201909:00:00");
        assert.strictEqual(list.$('.o_data_row:nth(1).o_data_cell').text(),"10/02/201909:00:00");

        list.destroy();
    });

    QUnit.test('datetimefieldremovevalue',asyncfunction(assert){
        assert.expect(4);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners"><fieldname="datetime"/></form>',
            res_id:1,
            mockRPC:function(route,args){
                if(route==='/web/dataset/call_kw/partner/write'){
                    assert.strictEqual(args.args[1].datetime,false,'thecorrectvalueshouldbesaved');
                }
                returnthis._super.apply(this,arguments);
            },
            translateParameters:{ //Avoidissuesduetolocalizationformats
                date_format:'%m/%d/%Y',
                time_format:'%H:%M:%S',
            },
            session:{
                getTZOffset:function(){
                    return120;
                },
            },
        });

        //switchtoeditmode
        awaittestUtils.form.clickEdit(form);
        assert.strictEqual(form.$('.o_datepicker_input').val(),'02/08/201712:00:00',
            'thedatetimeshouldbecorrectineditmode');

        awaittestUtils.fields.editAndTrigger($('.o_datepicker_input'),'',['input','change','focusout']);
        assert.strictEqual(form.$('.o_datepicker_input').val(),'',
            "shouldhaveanemptyinput");

        //save
        awaittestUtils.form.clickSave(form);
        assert.strictEqual(form.$('.o_field_date').text(),'',
            'theselecteddateshouldbedisplayedaftersaving');

        form.destroy();
    });

    QUnit.test('datetimefieldwithdate/datetimewidget(withdaychange)',asyncfunction(assert){
        assert.expect(2);

        this.data.partner.records[0].p=[2];
        this.data.partner.records[1].datetime="2017-02-0802:00:00";//UTC

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<fieldname="p">'+
                        '<tree>'+
                            '<fieldname="datetime"/>'+
                        '</tree>'+
                        '<form>'+
                            '<fieldname="datetime"widget="date"/>'+
                        '</form>'+
                     '</field>'+
                 '</form>',
            res_id:1,
            translateParameters:{ //Avoidissuesduetolocalizationformats
                date_format:'%m/%d/%Y',
                time_format:'%H:%M:%S',
            },
            session:{
                getTZOffset:function(){
                    return-240;
                },
            },
        });

        varexpectedDateString="02/07/201722:00:00";//localtimezone
        assert.strictEqual(form.$('.o_field_widget[name=p].o_data_cell').text(),expectedDateString,
            'thedatetime(datetimewidget)shouldbecorrectlydisplayedintreeview');

        //switchtoformview
        awaittestUtils.dom.click(form.$('.o_field_widget[name=p].o_data_row'));
        assert.strictEqual($('.modal.o_field_date[name=datetime]').text(),'02/07/2017',
            'thedatetime(datewidget)shouldbecorrectlydisplayedinformview');

        form.destroy();
    });

    QUnit.test('datetimefieldwithdate/datetimewidget(withoutdaychange)',asyncfunction(assert){
        assert.expect(2);

        this.data.partner.records[0].p=[2];
        this.data.partner.records[1].datetime="2017-02-0810:00:00";//withouttimezone

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<fieldname="p">'+
                        '<tree>'+
                            '<fieldname="datetime"/>'+
                        '</tree>'+
                        '<form>'+
                            '<fieldname="datetime"widget="date"/>'+
                        '</form>'+
                     '</field>'+
                 '</form>',
            res_id:1,
            translateParameters:{ //Avoidissuesduetolocalizationformats
                date_format:'%m/%d/%Y',
                time_format:'%H:%M:%S',
            },
            session:{
                getTZOffset:function(){
                    return-240;
                },
            },
        });

        varexpectedDateString="02/08/201706:00:00";//withtimezone
        assert.strictEqual(form.$('.o_field_widget[name=p].o_data_cell').text(),expectedDateString,
            'thedatetime(datetimewidget)shouldbecorrectlydisplayedintreeview');

        //switchtoformview
        awaittestUtils.dom.click(form.$('.o_field_widget[name=p].o_data_row'));
        assert.strictEqual($('.modal.o_field_date[name=datetime]').text(),'02/08/2017',
            'thedatetime(datewidget)shouldbecorrectlydisplayedinformview');

        form.destroy();
    });

    QUnit.test('datepickeroption:daysOfWeekDisabled',asyncfunction(assert){
        assert.expect(42);

        this.data.partner.fields.datetime.default="2017-08-0212:00:05";
        this.data.partner.fields.datetime.required=true;

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<fieldname="datetime"'+
                            'options=\'{"datepicker":{"daysOfWeekDisabled":[0,6]}}\'/>'+
                '</form>',
            res_id:1,
        });

        awaittestUtils.form.clickCreate(form);
        testUtils.dom.openDatepicker(form.$('.o_datepicker'));
        $.each($('.day:last-child,.day:nth-child(2)'),function(index,value){
            assert.hasClass(value,'disabled','firstandlastdaysmustbedisabled');
        });
        //theassertionsbelowcouldbereplacedbyasinglehasClassclassiconthejQuerysetusingtheidea
        //Allnot<=>notExists.Butwewanttobesurethatthesetisnonempty.Wedon'thaveanhelper
        //functionforthat.
        $.each($('.day:not(:last-child):not(:nth-child(2))'),function(index,value){
            assert.doesNotHaveClass(value,'disabled','otherdaysmuststayclickable');
        });
        form.destroy();
    });

    QUnit.test('datetimefield:hitentershouldupdatevalue',asyncfunction(assert){
        /*
        Thistestverifiesthatthefielddatetimeiscorrectlycomputedwhen:
            -wepressentertovalidateourentry
            -weclickoutsidethefieldtovalidateourentry
            -wesave
        */
        assert.expect(3);

        constform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners"><fieldname="datetime"/></form>',
            res_id:1,
            translateParameters:{ //Avoidissuesduetolocalizationformats
                date_format:'%m/%d/%Y',
                time_format:'%H:%M:%S',
            },
            viewOptions:{
                mode:'edit',
            },
            session:{
                getTZOffset:function(){
                    return120;
                },
            },
        });

        constdatetime=form.el.querySelector('input[name="datetime"]');

        //Enterabeginningofdateandpressentertovalidate
        awaittestUtils.fields.editInput(datetime,'01/08/2214:30:40');
        awaittestUtils.fields.triggerKeydown(datetime,'enter');

        constdatetimeValue=`01/08/202214:30:40`;

        assert.strictEqual(datetime.value,datetimeValue);

        //Clickoutsidethefieldtocheckthatthefieldisnotchanged
        awaittestUtils.dom.click(form.$el);
        assert.strictEqual(datetime.value,datetimeValue);

        //Saveandcheckthatit'sstillok
        awaittestUtils.form.clickSave(form);

        const{textContent}=form.el.querySelector('span[name="datetime"]')
        assert.strictEqual(textContent,datetimeValue);

        form.destroy();
    });

    QUnit.test('datetimefieldwithdatewidget:hitentershouldupdatevalue',asyncfunction(assert){
        assert.expect(2);

        constform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners"><fieldname="datetime"widget="date"/></form>',
            res_id:1,
            translateParameters:{ //Avoidissuesduetolocalizationformats
                date_format:'%m/%d/%Y',
            },
            viewOptions:{
                mode:'edit',
            },
            session:{
                getTZOffset:function(){
                    return120;
                },
            },
        });

        constdatetime=form.el.querySelector('input[name="datetime"]');

        awaittestUtils.fields.editInput(datetime,'01/08/22');
        awaittestUtils.fields.triggerKeydown(datetime,'enter');
        assert.strictEqual(datetime.value,'01/08/2022');

        //Clickoutsidethefieldtocheckthatthefieldisnotchanged
        awaittestUtils.dom.click(form.$el);
        assert.strictEqual(datetime.value,'01/08/2022');

        form.destroy();
    });

    QUnit.test("datetimefield:usepickerwitharabicnumberingsystem",asyncfunction(assert){
        assert.expect(2);

        constsymbols=[
            ["1","١"],
            ["2","٢"],
            ["3","٣"],
            ["4","٤"],
            ["5","٥"],
            ["6","٦"],
            ["7","٧"],
            ["8","٨"],
            ["9","٩"],
            ["0","٠"],
        ];
        constsymbolMap=Object.fromEntries(symbols);
        constnumberMap=Object.fromEntries(symbols.map(([latn,arab])=>[arab,latn]));

        constoriginalLocale=moment.locale();
        moment.defineLocale("TEST_ar",{
            preparse:
                (string)=>string
                    .replace(/\u200f/g,"")
                    .replace(/[١٢٣٤٥٦٧٨٩٠]/g,(match)=>numberMap[match])
                    .replace(/،/g,","),
            postformat:
                (string)=>string
                    .replace(/\d/g,(match)=>symbolMap[match])
                    .replace(/,/g,"،"),
        });

        constform=awaitcreateView({
            View:FormView,
            model:"partner",
            data:this.data,
            arch:/*xml*/`
                <formstring="Partners">
                    <fieldname="datetime"/>
                </form>
            `,
            res_id:1,
            viewOptions:{
                mode:"edit",
            },
        });

        constgetInput=()=>form.el.querySelector("[name=datetime]input")
        constclick=(el)=>testUtils.dom.click($(el));

        assert.strictEqual(getInput().value,"٠٢/٠٨/٢٠١٧١٠:٠٠:٠٠");

        awaitclick(getInput());

        awaitclick(document.querySelector("[data-action=togglePicker]"));

        awaitclick(document.querySelector("[data-action=showMinutes]"));
        awaitclick(document.querySelectorAll("[data-action=selectMinute]")[9]);

        awaitclick(document.querySelector("[data-action=showSeconds]"));
        awaitclick(document.querySelectorAll("[data-action=selectSecond]")[3]);

        assert.strictEqual(getInput().value,"٠٢/٠٨/٢٠١٧١٠:٤٥:١٥");

        moment.locale(originalLocale);
        moment.updateLocale("TEST_ar",null);

        form.destroy();
    })

    QUnit.module('RemainingDays');

    QUnit.test('remaining_dayswidgetonadatefieldinlistview',asyncfunction(assert){
        assert.expect(16);

        constunpatchDate=patchDate(2017,9,8,15,35,11);//October82017,15:35:11
        this.data.partner.records=[
            {id:1,date:'2017-10-08'},//today
            {id:2,date:'2017-10-09'},//tomorrow
            {id:3,date:'2017-10-07'},//yesterday
            {id:4,date:'2017-10-10'},//+2days
            {id:5,date:'2017-10-05'},//-3days
            {id:6,date:'2018-02-08'},//+4months(diff>=100days)
            {id:7,date:'2017-06-08'},//-4months(diff>=100days)
            {id:8,date:false},
        ];

        constlist=awaitcreateView({
            View:ListView,
            model:'partner',
            data:this.data,
            arch:'<tree><fieldname="date"widget="remaining_days"/></tree>',
        });

        assert.strictEqual(list.$('.o_data_cell:nth(0)').text(),'Today');
        assert.strictEqual(list.$('.o_data_cell:nth(1)').text(),'Tomorrow');
        assert.strictEqual(list.$('.o_data_cell:nth(2)').text(),'Yesterday');
        assert.strictEqual(list.$('.o_data_cell:nth(3)').text(),'In2days');
        assert.strictEqual(list.$('.o_data_cell:nth(4)').text(),'3daysago');
        assert.strictEqual(list.$('.o_data_cell:nth(5)').text(),'02/08/2018');
        assert.strictEqual(list.$('.o_data_cell:nth(6)').text(),'06/08/2017');
        assert.strictEqual(list.$('.o_data_cell:nth(7)').text(),'');

        assert.strictEqual(list.$('.o_data_cell:nth(0).o_field_widget').attr('title'),'10/08/2017');

        assert.hasClass(list.$('.o_data_cell:nth(0)div'),'text-bftext-warning');
        assert.doesNotHaveClass(list.$('.o_data_cell:nth(1)div'),'text-bftext-warningtext-danger');
        assert.hasClass(list.$('.o_data_cell:nth(2)div'),'text-bftext-danger');
        assert.doesNotHaveClass(list.$('.o_data_cell:nth(3)div'),'text-bftext-warningtext-danger');
        assert.hasClass(list.$('.o_data_cell:nth(4)div'),'text-bftext-danger');
        assert.doesNotHaveClass(list.$('.o_data_cell:nth(5)div'),'text-bftext-warningtext-danger');
        assert.hasClass(list.$('.o_data_cell:nth(6)div'),'text-bftext-danger');

        list.destroy();
        unpatchDate();
    });

    QUnit.test('remaining_dayswidgetonadatefieldinformview',asyncfunction(assert){
        assert.expect(4);

        constunpatchDate=patchDate(2017,9,8,15,35,11);//October82017,15:35:11
        this.data.partner.records=[
            {id:1,date:'2017-10-08'},//today
        ];

        constform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<form><fieldname="date"widget="remaining_days"/></form>',
            res_id:1,
        });

        assert.strictEqual(form.$('.o_field_widget').text(),'Today');
        assert.hasClass(form.$('.o_field_widget'),'text-bftext-warning');

        //ineditmode,thiswidgetshouldnotbeeditable.
        awaittestUtils.form.clickEdit(form);

        assert.hasClass(form.$('.o_form_view'),'o_form_editable');
        assert.containsOnce(form,'div.o_field_widget[name=date]');

        form.destroy();
        unpatchDate();
    });

    QUnit.test('remaining_dayswidgetonadatetimefieldinlistviewinUTC',asyncfunction(assert){
        assert.expect(16);

        constunpatchDate=patchDate(2017,9,8,15,35,11);//October82017,15:35:11
        this.data.partner.records=[
            {id:1,datetime:'2017-10-0820:00:00'},//today
            {id:2,datetime:'2017-10-0908:00:00'},//tomorrow
            {id:3,datetime:'2017-10-0718:00:00'},//yesterday
            {id:4,datetime:'2017-10-1022:00:00'},//+2days
            {id:5,datetime:'2017-10-0504:00:00'},//-3days
            {id:6,datetime:'2018-02-0804:00:00'},//+4months(diff>=100days)
            {id:7,datetime:'2017-06-0804:00:00'},//-4months(diff>=100days)
            {id:8,datetime:false},
        ];

        constlist=awaitcreateView({
            View:ListView,
            model:'partner',
            data:this.data,
            arch:'<tree><fieldname="datetime"widget="remaining_days"/></tree>',
            session:{
                getTZOffset:()=>0,
            },
        });

        assert.strictEqual(list.$('.o_data_cell:nth(0)').text(),'Today');
        assert.strictEqual(list.$('.o_data_cell:nth(1)').text(),'Tomorrow');
        assert.strictEqual(list.$('.o_data_cell:nth(2)').text(),'Yesterday');
        assert.strictEqual(list.$('.o_data_cell:nth(3)').text(),'In2days');
        assert.strictEqual(list.$('.o_data_cell:nth(4)').text(),'3daysago');
        assert.strictEqual(list.$('.o_data_cell:nth(5)').text(),'02/08/2018');
        assert.strictEqual(list.$('.o_data_cell:nth(6)').text(),'06/08/2017');
        assert.strictEqual(list.$('.o_data_cell:nth(7)').text(),'');

        assert.strictEqual(list.$('.o_data_cell:nth(0).o_field_widget').attr('title'),'10/08/2017');

        assert.hasClass(list.$('.o_data_cell:nth(0)div'),'text-bftext-warning');
        assert.doesNotHaveClass(list.$('.o_data_cell:nth(1)div'),'text-bftext-warningtext-danger');
        assert.hasClass(list.$('.o_data_cell:nth(2)div'),'text-bftext-danger');
        assert.doesNotHaveClass(list.$('.o_data_cell:nth(3)div'),'text-bftext-warningtext-danger');
        assert.hasClass(list.$('.o_data_cell:nth(4)div'),'text-bftext-danger');
        assert.doesNotHaveClass(list.$('.o_data_cell:nth(5)div'),'text-bftext-warningtext-danger');
        assert.hasClass(list.$('.o_data_cell:nth(6)div'),'text-bftext-danger');

        list.destroy();
        unpatchDate();
    });

    QUnit.test('remaining_dayswidgetonadatetimefieldinlistviewinUTC+6',asyncfunction(assert){
        assert.expect(6);

        constunpatchDate=patchDate(2017,9,8,15,35,11);//October82017,15:35:11,UTC+6
        this.data.partner.records=[
            {id:1,datetime:'2017-10-0820:00:00'},//tomorrow
            {id:2,datetime:'2017-10-0908:00:00'},//tomorrow
            {id:3,datetime:'2017-10-0718:30:00'},//today
            {id:4,datetime:'2017-10-0712:00:00'},//yesterday
            {id:5,datetime:'2017-10-0920:00:00'},//+2days
        ];

        constlist=awaitcreateView({
            View:ListView,
            model:'partner',
            data:this.data,
            arch:'<tree><fieldname="datetime"widget="remaining_days"/></tree>',
            session:{
                getTZOffset:()=>360,
            },
        });

        assert.strictEqual(list.$('.o_data_cell:nth(0)').text(),'Tomorrow');
        assert.strictEqual(list.$('.o_data_cell:nth(1)').text(),'Tomorrow');
        assert.strictEqual(list.$('.o_data_cell:nth(2)').text(),'Today');
        assert.strictEqual(list.$('.o_data_cell:nth(3)').text(),'Yesterday');
        assert.strictEqual(list.$('.o_data_cell:nth(4)').text(),'In2days');

        assert.strictEqual(list.$('.o_data_cell:nth(0).o_field_widget').attr('title'),'10/09/2017');

        list.destroy();
        unpatchDate();
    });

    QUnit.test('remaining_dayswidgetonadatefieldinlistviewinUTC-6',asyncfunction(assert){
        assert.expect(6);

        constunpatchDate=patchDate(2017,9,8,15,35,11);//October82017,15:35:11
        this.data.partner.records=[
            {id:1,date:'2017-10-08'},//today
            {id:2,date:'2017-10-09'},//tomorrow
            {id:3,date:'2017-10-07'},//yesterday
            {id:4,date:'2017-10-10'},//+2days
            {id:5,date:'2017-10-05'},//-3days
        ];

        constlist=awaitcreateView({
            View:ListView,
            model:'partner',
            data:this.data,
            arch:'<tree><fieldname="date"widget="remaining_days"/></tree>',
            session:{
                getTZOffset:()=>-360,
            },
        });

        assert.strictEqual(list.$('.o_data_cell:nth(0)').text(),'Today');
        assert.strictEqual(list.$('.o_data_cell:nth(1)').text(),'Tomorrow');
        assert.strictEqual(list.$('.o_data_cell:nth(2)').text(),'Yesterday');
        assert.strictEqual(list.$('.o_data_cell:nth(3)').text(),'In2days');
        assert.strictEqual(list.$('.o_data_cell:nth(4)').text(),'3daysago');

        assert.strictEqual(list.$('.o_data_cell:nth(0).o_field_widget').attr('title'),'10/08/2017');

        list.destroy();
        unpatchDate();
    });

    QUnit.test('remaining_dayswidgetonadatetimefieldinlistviewinUTC-8',asyncfunction(assert){
        assert.expect(5);

        constunpatchDate=patchDate(2017,9,8,15,35,11);//October82017,15:35:11,UTC-8
        this.data.partner.records=[
            {id:1,datetime:'2017-10-0820:00:00'},//today
            {id:2,datetime:'2017-10-0907:00:00'},//today
            {id:3,datetime:'2017-10-0910:00:00'},//tomorrow
            {id:4,datetime:'2017-10-0806:00:00'},//yesterday
            {id:5,datetime:'2017-10-0702:00:00'},//-2days
        ];

        constlist=awaitcreateView({
            View:ListView,
            model:'partner',
            data:this.data,
            arch:'<tree><fieldname="datetime"widget="remaining_days"/></tree>',
            session:{
                getTZOffset:()=>-560,
            },
        });

        assert.strictEqual(list.$('.o_data_cell:nth(0)').text(),'Today');
        assert.strictEqual(list.$('.o_data_cell:nth(1)').text(),'Today');
        assert.strictEqual(list.$('.o_data_cell:nth(2)').text(),'Tomorrow');
        assert.strictEqual(list.$('.o_data_cell:nth(3)').text(),'Yesterday');
        assert.strictEqual(list.$('.o_data_cell:nth(4)').text(),'2daysago');

        list.destroy();
        unpatchDate();
    });

    QUnit.module('FieldMonetary');

    QUnit.test('monetaryfieldinformview',asyncfunction(assert){
        assert.expect(5);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<sheet>'+
                        '<fieldname="qux"widget="monetary"/>'+
                        '<fieldname="currency_id"invisible="1"/>'+
                    '</sheet>'+
                '</form>',
            res_id:5,
            session:{
                currencies:_.indexBy(this.data.currency.records,'id'),
            },
        });

        //Non-breakingspacebetweenthecurrencyandtheamount
        assert.strictEqual(form.$('.o_field_widget').first().text(),'$\u00a09.10',
            'Thevalueshouldbedisplayedproperly.');

        awaittestUtils.form.clickEdit(form);
        assert.strictEqual(form.$('.o_field_widget[name=qux]input').val(),'9.10',
            'Theinputshouldberenderedwithoutthecurrencysymbol.');
        assert.strictEqual(form.$('.o_field_widget[name=qux]input').parent().children().first().text(),'$',
            'Theinputshouldbeprecededbyaspancontainingthecurrencysymbol.');

        awaittestUtils.fields.editInput(form.$('.o_field_monetaryinput'),'108.2458938598598');
        assert.strictEqual(form.$('.o_field_widget[name=qux]input').val(),'108.2458938598598',
            'Thevalueshouldnotbeformatedyet.');

        awaittestUtils.form.clickSave(form);
        //Non-breakingspacebetweenthecurrencyandtheamount
        assert.strictEqual(form.$('.o_field_widget').first().text(),'$\u00a0108.25',
            'Thenewvalueshouldberoundedproperly.');

        form.destroy();
    });

    QUnit.test('monetaryfieldinthelinesofaformview',asyncfunction(assert){
        assert.expect(4);

        varform=awaitcreateView({
            View:FormView,
            model:'team',
            data:this.data,
            arch:'<form>'+
                    '<sheet>'+
                      '<fieldname="partner_ids">'+
                        '<treeeditable="bottom">'+
                          '<fieldname="monetary"/>'+
                          '<fieldname="currency_id"invisible="1"/>'+
                        '</tree>'+
                      '</field>'+
                    '</sheet>'+
                '</form>',
            res_id:1,
            session:{
                currencies:_.indexBy(this.data.currency.records,'id'),
            },
        });

        //Non-breakingspacebetweenthecurrencyandtheamount
        assert.strictEqual(form.$('.o_list_table.o_list_number').first().text(),'$\u00a099.9',
                           'Thevalueshouldbedisplayedproperly.');
        assert.hasAttrValue(form.$('.o_list_table.o_list_number').first(),'title','$\u00a099.9',
                           'Thetitlevalueshouldbedisplayedproperly.');

        awaittestUtils.form.clickEdit(form);

        //Non-breakingspacebetweenthecurrencyandtheamount
        assert.strictEqual(form.$('.o_list_table.o_list_number').first().text(),'$\u00a099.9',
                           'Thevalueshouldbedisplayedproperly.');
        assert.hasAttrValue(form.$('.o_list_table.o_list_number').first(),'title','$\u00a099.9',
                            'Thetitlevalueshouldbedisplayedproperly.');

        form.destroy();
    });

    QUnit.test('monetaryfieldroundingusingformulainformview',asyncfunction(assert){
        assert.expect(1);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<sheet>'+
                        '<fieldname="qux"widget="monetary"/>'+
                        '<fieldname="currency_id"invisible="1"/>'+
                    '</sheet>'+
                '</form>',
            res_id:5,
            session:{
                currencies:_.indexBy(this.data.currency.records,'id'),
            },
        });

        //Testcomputationandrounding
        awaittestUtils.form.clickEdit(form);
        awaittestUtils.fields.editInput(form.$('.o_field_monetaryinput'),'=100/3');
        awaittestUtils.form.clickSave(form);
        assert.strictEqual(form.$('.o_field_widget').first().text(),'$\u00a033.33',
            'Thenewvalueshouldbecalculatedandroundedproperly.');

        form.destroy();
    });

    QUnit.test('monetaryfieldwithcurrencysymbolafter',asyncfunction(assert){
        assert.expect(5);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<sheet>'+
                        '<fieldname="qux"widget="monetary"/>'+
                        '<fieldname="currency_id"invisible="1"/>'+
                    '</sheet>'+
                '</form>',
            res_id:2,
            session:{
                currencies:_.indexBy(this.data.currency.records,'id'),
            },
        });

        //Non-breakingspacebetweenthecurrencyandtheamount
        assert.strictEqual(form.$('.o_field_widget').first().text(),'0.00\u00a0€',
            'Thevalueshouldbedisplayedproperly.');

        awaittestUtils.form.clickEdit(form);
        assert.strictEqual(form.$('.o_field_widget[name=qux]input').val(),'0.00',
            'Theinputshouldberenderedwithoutthecurrencysymbol.');
        assert.strictEqual(form.$('.o_field_widget[name=qux]input').parent().children().eq(1).text(),'€',
            'Theinputshouldbefollowedbyaspancontainingthecurrencysymbol.');

        awaittestUtils.fields.editInput(form.$('.o_field_widget[name=qux]input'),'108.2458938598598');
        assert.strictEqual(form.$('.o_field_widget[name=qux]input').val(),'108.2458938598598',
            'Thevalueshouldnotbeformatedyet.');

        awaittestUtils.form.clickSave(form);
        //Non-breakingspacebetweenthecurrencyandtheamount
        assert.strictEqual(form.$('.o_field_widget').first().text(),'108.25\u00a0€',
            'Thenewvalueshouldberoundedproperly.');

        form.destroy();
    });

    QUnit.test('monetaryfieldwithcurrencydigits!=2',asyncfunction(assert){
        assert.expect(5);

        this.data.partner.records=[{
            id:1,
            bar:false,
            foo:"pouet",
            int_field:68,
            qux:99.1234,
            currency_id:1,
        }];
        this.data.currency.records=[{
            id:1,
            display_name:"VEF",
            symbol:"Bs.F",
            position:"after",
            digits:[16,4],
        }];

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<sheet>'+
                        '<fieldname="qux"widget="monetary"/>'+
                        '<fieldname="currency_id"invisible="1"/>'+
                    '</sheet>'+
                '</form>',
            res_id:1,
            session:{
                currencies:_.indexBy(this.data.currency.records,'id'),
            },
        });

        //Non-breakingspacebetweenthecurrencyandtheamount
        assert.strictEqual(form.$('.o_field_widget').first().text(),'99.1234\u00a0Bs.F',
            'Thevalueshouldbedisplayedproperly.');

        awaittestUtils.form.clickEdit(form);
        assert.strictEqual(form.$('.o_field_widget[name=qux]input').val(),'99.1234',
            'Theinputshouldberenderedwithoutthecurrencysymbol.');
        assert.strictEqual(form.$('.o_field_widget[name=qux]input').parent().children().eq(1).text(),'Bs.F',
            'Theinputshouldbefollowedbyaspancontainingthecurrencysymbol.');

        awaittestUtils.fields.editInput(form.$('.o_field_widget[name=qux]input'),'99.111111111');
        assert.strictEqual(form.$('.o_field_widget[name=qux]input').val(),'99.111111111',
            'Thevalueshouldnotbeformatedyet.');

        awaittestUtils.form.clickSave(form);
        //Non-breakingspacebetweenthecurrencyandtheamount
        assert.strictEqual(form.$('.o_field_widget').first().text(),'99.1111\u00a0Bs.F',
            'Thenewvalueshouldberoundedproperly.');

        form.destroy();
    });

    QUnit.test('monetaryfieldineditablelistview',asyncfunction(assert){
        assert.expect(9);

        varlist=awaitcreateView({
            View:ListView,
            model:'partner',
            data:this.data,
            arch:'<treeeditable="bottom">'+
                    '<fieldname="qux"widget="monetary"/>'+
                    '<fieldname="currency_id"invisible="1"/>'+
                  '</tree>',
            session:{
                currencies:_.indexBy(this.data.currency.records,'id'),
            },
        });

        vardollarValues=list.$('td').filter(function(){return_.str.include($(this).text(),'$');});
        assert.strictEqual(dollarValues.length,1,
            'Onlyonelinehasdollarasacurrency.');

        vareuroValues=list.$('td').filter(function(){return_.str.include($(this).text(),'€');});
        assert.strictEqual(euroValues.length,1,
            'Oneonelinehaseuroasacurrency.');

        varzeroValues=list.$('td.o_data_cell').filter(function(){return$(this).text()==='';});
        assert.strictEqual(zeroValues.length,1,
            'Unsetfloatvaluesshouldberenderedasemptystrings.');

        //switchtoeditmode
        var$cell=list.$('tr.o_data_rowtd:not(.o_list_record_selector):contains($)');
        awaittestUtils.dom.click($cell);

        assert.strictEqual($cell.children().length,1,
            'Thecelltdshouldonlycontainthespecialdivofmonetarywidget.');
        assert.containsOnce(list,'[name="qux"]input',
            'Theviewshouldhave1inputforeditablemonetaryfloat.');
        assert.strictEqual(list.$('[name="qux"]input').val(),'9.10',
            'Theinputshouldberenderedwithoutthecurrencysymbol.');
        assert.strictEqual(list.$('[name="qux"]input').parent().children().first().text(),'$',
            'Theinputshouldbeprecededbyaspancontainingthecurrencysymbol.');

        awaittestUtils.fields.editInput(list.$('[name="qux"]input'),'108.2458938598598');
        assert.strictEqual(list.$('[name="qux"]input').val(),'108.2458938598598',
            'Thetypedvalueshouldbecorrectlydisplayed.');

        awaittestUtils.dom.click(list.$buttons.find('.o_list_button_save'));
        assert.strictEqual(list.$('tr.o_data_rowtd:not(.o_list_record_selector):contains($)').text(),'$\u00a0108.25',
            'Thenewvalueshouldberoundedproperly.');

        list.destroy();
    });

    QUnit.test('monetaryfieldwithrealmonetaryfieldinmodel',asyncfunction(assert){
        assert.expect(7);

        this.data.partner.fields.qux.type="monetary";
        this.data.partner.fields.quux={
            string:"Quux",type:"monetary",digits:[16,1],searchable:true,readonly:true,
        };

        (_.find(this.data.partner.records,function(record){returnrecord.id===5;})).quux=4.2;

        this.data.partner.onchanges={
            bar:function(obj){
                obj.qux=obj.bar?100:obj.qux;
            },
        };

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<sheet>'+
                        '<fieldname="qux"/>'+
                        '<fieldname="quux"/>'+
                        '<fieldname="currency_id"/>'+
                        '<fieldname="bar"/>'+
                    '</sheet>'+
                '</form>',
            res_id:5,
            session:{
                currencies:_.indexBy(this.data.currency.records,'id'),
            },
        });

        assert.strictEqual(form.$('.o_field_monetary').first().html(),"$&nbsp;9.10",
            "readonlyvalueshouldcontainthecurrency");
        assert.strictEqual(form.$('.o_field_monetary').first().next().html(),"$&nbsp;4.20",
            "readonlyvalueshouldcontainthecurrency");

        awaittestUtils.form.clickEdit(form);

        assert.strictEqual(form.$('.o_field_monetary>input').val(),"9.10",
            "inputvalueineditionshouldonlycontainthevalue,withoutthecurrency");

        awaittestUtils.dom.click(form.$('input[type="checkbox"]'));
        assert.containsOnce(form,'.o_field_monetary>input',
            "Aftertheonchange,themonetary<input/>shouldnothavebeenduplicated");
        assert.containsOnce(form,'.o_field_monetary[name=quux]',
            "Aftertheonchange,themonetaryreadonlyfieldshouldnothavebeenduplicated");

        awaittestUtils.fields.many2one.clickOpenDropdown('currency_id');
        awaittestUtils.fields.many2one.clickItem('currency_id','€');
        assert.strictEqual(form.$('.o_field_monetary>span').html(),"€",
            "Aftercurrencychange,themonetaryfieldcurrencyshouldhavebeenupdated");
        assert.strictEqual(form.$('.o_field_monetary').first().next().html(),"4.20&nbsp;€",
            "readonlyvalueshouldcontaintheupdatedcurrency");

        form.destroy();
    });

    QUnit.test('monetaryfieldwithmonetaryfieldgiveninoptions',asyncfunction(assert){
        assert.expect(1);

        this.data.partner.fields.qux.type="monetary";
        this.data.partner.fields.company_currency_id={
            string:"CompanyCurrency",type:"many2one",relation:"currency",
        };
        this.data.partner.records[4].company_currency_id=2;

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<sheet>'+
                        '<fieldname="qux"options="{\'currency_field\':\'company_currency_id\'}"/>'+
                        '<fieldname="company_currency_id"/>'+
                    '</sheet>'+
                '</form>',
            res_id:5,
            session:{
                currencies:_.indexBy(this.data.currency.records,'id'),
            },
        });

        assert.strictEqual(form.$('.o_field_monetary').html(),"9.10&nbsp;€",
            "fieldmonetaryshouldbeformattedwithcorrectcurrency");

        form.destroy();
    });

    QUnit.test('shouldkeepthefocuswhenbeingeditedinx2manylists',asyncfunction(assert){
        assert.expect(6);

        this.data.partner.fields.currency_id.default=1;
        this.data.partner.fields.m2m={
            string:"m2m",type:"many2many",relation:'partner',default:[[6,false,[2]]],
        };
        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<sheet>'+
                        '<fieldname="p"/>'+
                        '<fieldname="m2m"/>'+
                    '</sheet>'+
                '</form>',
            archs:{
                'partner,false,list':'<treeeditable="bottom">'+
                    '<fieldname="qux"widget="monetary"/>'+
                    '<fieldname="currency_id"invisible="1"/>'+
                '</tree>',
            },
            session:{
                currencies:_.indexBy(this.data.currency.records,'id'),
            },
        });

        //testthemonetaryfieldinsidetheone2many
        var$o2m=form.$('.o_field_widget[name=p]');
        awaittestUtils.dom.click($o2m.find('.o_field_x2many_list_row_adda'));
        awaittestUtils.fields.editInput($o2m.find('.o_field_widgetinput'),"22");

        assert.strictEqual($o2m.find('.o_field_widgetinput').get(0),document.activeElement,
            "thefocusshouldstillbeontheinput");
        assert.strictEqual($o2m.find('.o_field_widgetinput').val(),"22",
            "thevalueshouldnothavebeenformattedyet");

        awaittestUtils.dom.click(form.$el);

        assert.strictEqual($o2m.find('.o_field_widget[name=qux]').html(),"$&nbsp;22.00",
            "thevalueshouldhavebeenformattedafterlosingthefocus");

        //testthemonetaryfieldinsidethemany2many
        var$m2m=form.$('.o_field_widget[name=m2m]');
        awaittestUtils.dom.click($m2m.find('.o_data_rowtd:first'));
        awaittestUtils.fields.editInput($m2m.find('.o_field_widgetinput'),"22");

        assert.strictEqual($m2m.find('.o_field_widgetinput').get(0),document.activeElement,
            "thefocusshouldstillbeontheinput");
        assert.strictEqual($m2m.find('.o_field_widgetinput').val(),"22",
            "thevalueshouldnothavebeenformattedyet");

        awaittestUtils.dom.click(form.$el);

        assert.strictEqual($m2m.find('.o_field_widget[name=qux]').html(),"22.00&nbsp;€",
            "thevalueshouldhavebeenformattedafterlosingthefocus");

        form.destroy();
    });

    QUnit.test('monetaryfieldwithcurrencysetbyanonchange',asyncfunction(assert){
        //thistestensuresthatthemonetaryfieldcanbere-renderedwithand
        //withoutcurrency(whichcanhappenasthecurrencycanbesetbyan
        //onchange)
        assert.expect(8);

        this.data.partner.onchanges={
            int_field:function(obj){
                obj.currency_id=obj.int_field?2:null;
            },
        };

        varlist=awaitcreateView({
            View:ListView,
            model:'partner',
            data:this.data,
            arch:'<treeeditable="top">'+
                        '<fieldname="int_field"/>'+
                        '<fieldname="qux"widget="monetary"/>'+
                        '<fieldname="currency_id"invisible="1"/>'+
                    '</tree>',
            session:{
                currencies:_.indexBy(this.data.currency.records,'id'),
            },
        });

        awaittestUtils.dom.click(list.$buttons.find('.o_list_button_add'));
        assert.containsOnce(list,'div.o_field_widget[name=qux]input',
            "monetaryfieldshouldhavebeenrenderedcorrectly(withoutcurrency)");
        assert.containsNone(list,'.o_field_widget[name=qux]span',
            "monetaryfieldshouldhavebeenrenderedcorrectly(withoutcurrency)");

        //setavalueforint_field->shouldsetthecurrencyandre-renderqux
        awaittestUtils.fields.editInput(list.$('.o_field_widget[name=int_field]'),'7');
        assert.containsOnce(list,'div.o_field_widget[name=qux]input',
            "monetaryfieldshouldhavebeenre-renderedcorrectly(withcurrency)");
        assert.strictEqual(list.$('.o_field_widget[name=qux]span:contains(€)').length,1,
            "monetaryfieldshouldhavebeenre-renderedcorrectly(withcurrency)");
        var$quxInput=list.$('.o_field_widget[name=qux]input');
        awaittestUtils.dom.click($quxInput);
        assert.strictEqual(document.activeElement,$quxInput[0],
            "focusshouldbeonthequxfield'sinput");

        //unsetthevalueofint_field->shouldunsetthecurrencyandre-renderqux
        awaittestUtils.dom.click(list.$('.o_field_widget[name=int_field]'));
        awaittestUtils.fields.editInput(list.$('.o_field_widget[name=int_field]'),'0');
        $quxInput=list.$('div.o_field_widget[name=qux]input');
        assert.strictEqual($quxInput.length,1,
            "monetaryfieldshouldhavebeenre-renderedcorrectly(withoutcurrency)");
        assert.containsNone(list,'.o_field_widget[name=qux]span',
            "monetaryfieldshouldhavebeenre-renderedcorrectly(withoutcurrency)");
        awaittestUtils.dom.click($quxInput);
        assert.strictEqual(document.activeElement,$quxInput[0],
            "focusshouldbeonthequxfield'sinput");

        list.destroy();
    });

    QUnit.module('FieldInteger');

    QUnit.test('integerfieldwhenunset',asyncfunction(assert){
        assert.expect(2);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners"><fieldname="int_field"/></form>',
            res_id:4,
        });

        assert.doesNotHaveClass(form.$('.o_field_widget'),'o_field_empty',
            'Non-setintegerfieldshouldberecognizedas0.');
        assert.strictEqual(form.$('.o_field_widget').text(),"0",
            'Non-setintegerfieldshouldberecognizedas0.');

        form.destroy();
    });

    QUnit.test('integerfieldinformview',asyncfunction(assert){
        assert.expect(4);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners"><fieldname="int_field"/></form>',
            res_id:2,
        });

        assert.doesNotHaveClass(form.$('.o_field_widget'),'o_field_empty',
            'Integerfieldshouldbeconsideredsetforvalue0.');

        awaittestUtils.form.clickEdit(form);
        assert.strictEqual(form.$('input[name=int_field]').val(),'0',
            'Thevalueshouldberenderedcorrectlyineditmode.');

        awaittestUtils.fields.editInput(form.$('input[name=int_field]'),'-18');
        assert.strictEqual(form.$('input[name=int_field]').val(),'-18',
            'Thevalueshouldbecorrectlydisplayedintheinput.');

        awaittestUtils.form.clickSave(form);
        assert.strictEqual(form.$('.o_field_widget').text(),'-18',
            'Thenewvalueshouldbesavedanddisplayedproperly.');

        form.destroy();
    });

    QUnit.test('integerfieldroundingusingformulainformview',asyncfunction(assert){
        assert.expect(1);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners"><fieldname="int_field"/></form>',
            res_id:2,
        });

        //Testcomputationandrounding
        awaittestUtils.form.clickEdit(form);
        awaittestUtils.fields.editInput(form.$('input[name=int_field]'),'=100/3');
        awaittestUtils.form.clickSave(form);
        assert.strictEqual(form.$('.o_field_widget').first().text(),'33',
            'Thenewvalueshouldbecalculatedproperly.');

        form.destroy();
    });

    QUnit.test('integerfieldinformviewwithvirtualid',asyncfunction(assert){
        assert.expect(1);
        varparams={
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners"><fieldname="id"/></form>',
        };

        params.res_id=this.data.partner.records[1].id="2-20170808020000";
        varform=awaitcreateView(params);
        assert.strictEqual(form.$('.o_field_widget').text(),"2-20170808020000",
            "Shoulddisplayvirtualid");

        form.destroy();
    });

    QUnit.test('integerfieldineditablelistview',asyncfunction(assert){
        assert.expect(4);

        varlist=awaitcreateView({
            View:ListView,
            model:'partner',
            data:this.data,
            arch:'<treeeditable="bottom">'+
                    '<fieldname="int_field"/>'+
                  '</tree>',
        });

        varzeroValues=list.$('td').filter(function(){return$(this).text()==='0';});
        assert.strictEqual(zeroValues.length,1,
            'Unsetintegervaluesshouldnotberenderedaszeros.');

        //switchtoeditmode
        var$cell=list.$('tr.o_data_rowtd:not(.o_list_record_selector)').first();
        awaittestUtils.dom.click($cell);

        assert.containsOnce(list,'input[name="int_field"]',
            'Theviewshouldhave1inputforeditableinteger.');

        awaittestUtils.fields.editInput(list.$('input[name="int_field"]'),'-28');
        assert.strictEqual(list.$('input[name="int_field"]').val(),'-28',
            'Thevalueshouldbedisplayedproperlyintheinput.');

        awaittestUtils.dom.click(list.$buttons.find('.o_list_button_save'));
        assert.strictEqual(list.$('td:not(.o_list_record_selector)').first().text(),'-28',
            'Thenewvalueshouldbesavedanddisplayedproperly.');

        list.destroy();
    });

    QUnit.test('integerfieldwithtypenumberoption',asyncfunction(assert){
        assert.expect(4);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                '<fieldname="int_field"options="{\'type\':\'number\'}"/>'+
            '</form>',
            res_id:4,
            translateParameters:{
                thousands_sep:",",
                grouping:[3,0],
            },
        });

        awaittestUtils.form.clickEdit(form);
        assert.ok(form.$('.o_field_widget')[0].hasAttribute('type'),
            'Integerfieldwithoptiontypemusthaveatypeattribute.');
        assert.hasAttrValue(form.$('.o_field_widget'),'type','number',
            'Integerfieldwithoptiontypemusthaveatypeattributeequalsto"number".');

        awaittestUtils.fields.editInput(form.$('input[name=int_field]'),'1234567890');
        awaittestUtils.form.clickSave(form);
        awaittestUtils.form.clickEdit(form);
        assert.strictEqual(form.$('.o_field_widget').val(),'1234567890',
            'Integervaluemustbenotformattedifinputtypeisnumber.');
        awaittestUtils.form.clickSave(form);
        assert.strictEqual(form.$('.o_field_widget').text(),'1,234,567,890',
            'Integervaluemustbeformattedinreadonlyvieweveniftheinputtypeisnumber.');

        form.destroy();
    });

    QUnit.test('integerfieldwithouttypenumberoption',asyncfunction(assert){
        assert.expect(2);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                '<fieldname="int_field"/>'+
            '</form>',
            res_id:4,
            translateParameters:{
                thousands_sep:",",
                grouping:[3,0],
            },
        });

        awaittestUtils.form.clickEdit(form);
        assert.hasAttrValue(form.$('.o_field_widget'),'type','text',
            'Integerfieldwithoutoptiontypemusthaveatexttype(defaulttype).');

        awaittestUtils.fields.editInput(form.$('input[name=int_field]'),'1234567890');
        awaittestUtils.form.clickSave(form);
        awaittestUtils.form.clickEdit(form);
        assert.strictEqual(form.$('.o_field_widget').val(),'1,234,567,890',
            'Integervaluemustbeformattedifinputtypeisn\'tnumber.');

        form.destroy();
    });

    QUnit.test('integerfieldwithoutformatting',asyncfunction(assert){
        assert.expect(3);

        this.data.partner.records=[{
            'id':999,
            'int_field':7073,
        }];

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                '<fieldname="int_field"options="{\'format\':\'false\'}"/>'+
            '</form>',
            res_id:999,
            translateParameters:{
                thousands_sep:",",
                grouping:[3,0],
            },
        });

        assert.ok(form.$('.o_form_view').hasClass('o_form_readonly'),'Forminreadonlymode');
        assert.strictEqual(form.$('.o_field_widget[name=int_field]').text(),'7073',
            'Integervaluemustnotbeformatted');
        awaittestUtils.form.clickEdit(form);

        assert.strictEqual(form.$('.o_field_widget').val(),'7073',
            'Integervaluemustnotbeformatted');

        form.destroy();
    });

    QUnit.test('integerfieldisformattedbydefault',asyncfunction(assert){
        assert.expect(3);

        this.data.partner.records=[{
            'id':999,
            'int_field':7073,
        }];

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                '<fieldname="int_field"/>'+
            '</form>',
            res_id:999,
            translateParameters:{
                thousands_sep:",",
                grouping:[3,0],
            },
        });
        assert.ok(form.$('.o_form_view').hasClass('o_form_readonly'),'Forminreadonlymode');
        assert.strictEqual(form.$('.o_field_widget[name=int_field]').text(),'8,069',
            'Integervaluemustbeformattedbydefault');
        awaittestUtils.form.clickEdit(form);

        assert.strictEqual(form.$('.o_field_widget').val(),'8,069',
            'Integervaluemustbeformattedbydefault');

        form.destroy();
    });

    QUnit.module('FieldFloatTime');

    QUnit.test('float_timefieldinformview',asyncfunction(assert){
        assert.expect(5);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<sheet>'+
                        '<fieldname="qux"widget="float_time"/>'+
                    '</sheet>'+
                '</form>',
            mockRPC:function(route,args){
                if(route==='/web/dataset/call_kw/partner/write'){
                    //48/60=0.8
                    assert.strictEqual(args.args[1].qux,-11.8,'thecorrectfloatvalueshouldbesaved');
                }
                returnthis._super.apply(this,arguments);
            },
            res_id:5,
        });

        //9+0.1*60=9.06
        assert.strictEqual(form.$('.o_field_widget').first().text(),'09:06',
            'Theformattedtimevalueshouldbedisplayedproperly.');

        awaittestUtils.form.clickEdit(form);
        assert.strictEqual(form.$('input[name=qux]').val(),'09:06',
            'Thevalueshouldberenderedcorrectlyintheinput.');

        awaittestUtils.fields.editInput(form.$('input[name=qux]'),'-11:48');
        assert.strictEqual(form.$('input[name=qux]').val(),'-11:48',
            'Thenewvalueshouldbedisplayedproperlyintheinput.');

        awaittestUtils.form.clickSave(form);
        assert.strictEqual(form.$('.o_field_widget').first().text(),'-11:48',
            'Thenewvalueshouldbesavedanddisplayedproperly.');

        form.destroy();
    });


    QUnit.module('FieldFloatFactor');

    QUnit.test('float_factorfieldinformview',asyncfunction(assert){
        assert.expect(4);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<sheet>'+
                        '<fieldname="qux"widget="float_factor"options="{\'factor\':0.5}"digits="[16,2]"/>'+
                    '</sheet>'+
                '</form>',
            mockRPC:function(route,args){
                if(route==='/web/dataset/call_kw/partner/write'){
                    //16.4/2=8.2
                    assert.strictEqual(args.args[1].qux,4.6,'thecorrectfloatvalueshouldbesaved');
                }
                returnthis._super.apply(this,arguments);
            },
            res_id:5,
        });
        assert.strictEqual(form.$('.o_field_widget').first().text(),'4.55',//9.1/0.5
            'Theformattedvalueshouldbedisplayedproperly.');

        awaittestUtils.form.clickEdit(form);
        assert.strictEqual(form.$('input[name=qux]').val(),'4.55',
            'Thevalueshouldberenderedcorrectlyintheinput.');

        awaittestUtils.fields.editInput(form.$('input[name=qux]'),'2.3');

        awaittestUtils.form.clickSave(form);
        assert.strictEqual(form.$('.o_field_widget').first().text(),'2.30',
            'Thenewvalueshouldbesavedanddisplayedproperly.');

        form.destroy();
    });

    QUnit.module('FieldFloatToggle');

    QUnit.test('float_togglefieldinformview',asyncfunction(assert){
        assert.expect(5);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<sheet>'+
                        '<fieldname="qux"widget="float_toggle"options="{\'factor\':0.125,\'range\':[0,1,0.75,0.5,0.25]}"digits="[5,3]"/>'+
                    '</sheet>'+
                '</form>',
            mockRPC:function(route,args){
                if(route==='/web/dataset/call_kw/partner/write'){
                    //1.000/0.125=8
                    assert.strictEqual(args.args[1].qux,8,'thecorrectfloatvalueshouldbesaved');
                }
                returnthis._super.apply(this,arguments);
            },
            res_id:1,
        });
        assert.strictEqual(form.$('.o_field_widget').first().text(),'0.056',
            'Theformattedtimevalueshouldbedisplayedproperly.');

        awaittestUtils.form.clickEdit(form);

        assert.strictEqual(form.$('button.o_field_float_toggle').text(),'0.056',
            'Thevalueshouldberenderedcorrectlyonthebutton.');

        awaittestUtils.dom.click(form.$('button.o_field_float_toggle'));

        assert.strictEqual(form.$('button.o_field_float_toggle').text(),'1.000',
            'Thevalueshouldberenderedcorrectlyonthebutton.');

        awaittestUtils.form.clickSave(form);

        assert.strictEqual(form.$('.o_field_widget').first().text(),'1.000',
            'Thenewvalueshouldbesavedanddisplayedproperly.');

        form.destroy();
    });


    QUnit.module('PhoneWidget');

    QUnit.test('phonefieldinformviewonnormalscreens',asyncfunction(assert){
        assert.expect(5);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<sheet>'+
                        '<group>'+
                            '<fieldname="foo"widget="phone"/>'+
                        '</group>'+
                    '</sheet>'+
                '</form>',
            res_id:1,
            config:{
                device:{
                    size_class:config.device.SIZES.LG,
                },
            },
        });

        var$phone=form.$('a.o_field_widget.o_form_uri');
        assert.strictEqual($phone.length,1,
            "shouldhaverenderedthephonenumberasalinkwithcorrectclasses");
        assert.strictEqual($phone.text(),'yop',
            "valueshouldbedisplayedproperly");

        //switchtoeditmodeandchecktheresult
        awaittestUtils.form.clickEdit(form);
        assert.containsOnce(form,'input[type="text"].o_field_widget',
            "shouldhaveaninputforthephonefield");
        assert.strictEqual(form.$('input[type="text"].o_field_widget').val(),'yop',
            "inputshouldcontainfieldvalueineditmode");

        //changevalueineditmode
        awaittestUtils.fields.editInput(form.$('input[type="text"].o_field_widget'),'new');

        //save
        awaittestUtils.form.clickSave(form);
        assert.strictEqual(form.$('a.o_field_widget.o_form_uri').text(),'new',
            "newvalueshouldbedisplayedproperly");

        form.destroy();
    });

    QUnit.test('phonefieldineditablelistviewonnormalscreens',asyncfunction(assert){
        assert.expect(8);
        vardoActionCount=0;

        varlist=awaitcreateView({
            View:ListView,
            model:'partner',
            data:this.data,
            arch:'<treeeditable="bottom"><fieldname="foo"widget="phone"/></tree>',
            config:{
                device:{
                    size_class:config.device.SIZES.LG,
                },
            },
        });

        assert.containsN(list,'tbodytd:not(.o_list_record_selector)',5);
        assert.strictEqual(list.$('tbodytd:not(.o_list_record_selector)a').first().text(),'yop',
            "valueshouldbedisplayedproperlywithalinktosendSMS");

        assert.containsN(list,'a.o_field_widget.o_form_uri',5,
            "shouldhavethecorrectclassnames");

        //Editalineandchecktheresult
        var$cell=list.$('tbodytd:not(.o_list_record_selector)').first();
        awaittestUtils.dom.click($cell);
        assert.hasClass($cell.parent(),'o_selected_row','shouldbesetaseditmode');
        assert.strictEqual($cell.find('input').val(),'yop',
            'shouldhavethecorectvalueininternalinput');
        awaittestUtils.fields.editInput($cell.find('input'),'new');

        //save
        awaittestUtils.dom.click(list.$buttons.find('.o_list_button_save'));
        $cell=list.$('tbodytd:not(.o_list_record_selector)').first();
        assert.doesNotHaveClass($cell.parent(),'o_selected_row','shouldnotbeineditmodeanymore');
        assert.strictEqual(list.$('tbodytd:not(.o_list_record_selector)a').first().text(),'new',
            "valueshouldbeproperlyupdated");
        assert.containsN(list,'a.o_field_widget.o_form_uri',5,
            "shouldstillhavelinkswithcorrectclasses");

        list.destroy();
    });

    QUnit.test('useTABtonavigatetoaphonefield',asyncfunction(assert){
        assert.expect(2);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<sheet>'+
                        '<group>'+
                            '<fieldname="display_name"/>'+
                            '<fieldname="foo"widget="phone"/>'+
                        '</group>'+
                    '</sheet>'+
                '</form>',
        });

        testUtils.dom.click(form.$('input[name=display_name]'));
        assert.strictEqual(form.$('input[name="display_name"]')[0],document.activeElement,
            "display_nameshouldbefocused");
        form.$('input[name="display_name"]').trigger($.Event('keydown',{which:$.ui.keyCode.TAB}));
        assert.strictEqual(form.$('input[name="foo"]')[0],document.activeElement,
            "fooshouldbefocused");

        form.destroy();
    });

    QUnit.module('PriorityWidget');

    QUnit.test('prioritywidgetwhennotset',asyncfunction(assert){
        assert.expect(4);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<sheet>'+
                        '<group>'+
                            '<fieldname="selection"widget="priority"/>'+
                        '</group>'+
                    '</sheet>'+
                '</form>',
            res_id:2,
        });

        assert.strictEqual(form.$('.o_field_widget.o_priority:not(.o_field_empty)').length,1,
            "widgetshouldbeconsideredset,eventhoughthereisnovalueforthisfield");
        assert.strictEqual(form.$('.o_field_widget.o_priority').find('a.o_priority_star').length,2,
            "shouldhavetwostarsforrepresentingeachpossiblevalue:nostar,onestarandtwostars");
        assert.strictEqual(form.$('.o_field_widget.o_priority').find('a.o_priority_star.fa-star').length,0,
            "shouldhavenofullstarsincethereisnovalue");
        assert.strictEqual(form.$('.o_field_widget.o_priority').find('a.o_priority_star.fa-star-o').length,2,
            "shouldhavetwoemptystarssincethereisnovalue");

        form.destroy();
    });

    QUnit.test('prioritywidgetinformview',asyncfunction(assert){
        assert.expect(22);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<sheet>'+
                        '<group>'+
                            '<fieldname="selection"widget="priority"/>'+
                        '</group>'+
                    '</sheet>'+
                '</form>',
            res_id:1,
        });

        assert.strictEqual(form.$('.o_field_widget.o_priority:not(.o_field_empty)').length,1,
            "widgetshouldbeconsideredset");
        assert.strictEqual(form.$('.o_field_widget.o_priority').find('a.o_priority_star').length,2,
            "shouldhavetwostarsforrepresentingeachpossiblevalue:nostar,onestarandtwostars");
        assert.strictEqual(form.$('.o_field_widget.o_priority').find('a.o_priority_star.fa-star').length,1,
            "shouldhaveonefullstarsincethevalueisthesecondvalue");
        assert.strictEqual(form.$('.o_field_widget.o_priority').find('a.o_priority_star.fa-star-o').length,1,
            "shouldhaveoneemptystarsincethevalueisthesecondvalue");

        //hoverlaststar
        form.$('.o_field_widget.o_prioritya.o_priority_star.fa-star-o').last().trigger('mouseover');
        assert.strictEqual(form.$('.o_field_widget.o_priority').find('a.o_priority_star').length,2,
            "shouldhavetwostarsforrepresentingeachpossiblevalue:nostar,onestarandtwostars");
        assert.strictEqual(form.$('.o_field_widget.o_priority').find('a.o_priority_star.fa-star').length,2,
            "shouldtemporaryhavetwofullstarssincewearehoveringthethirdvalue");
        assert.strictEqual(form.$('.o_field_widget.o_priority').find('a.o_priority_star.fa-star-o').length,0,
            "shouldtemporaryhavenoemptystarsincewearehoveringthethirdvalue");

        //Hereweshouldtestwithmouseout,butcurrentlytheeffectassociatedwithit
        //occursinasetTimeoutafter200mssoit'snottrivialtotestithere.

        //switchtoeditmodeandchecktheresult
        awaittestUtils.form.clickEdit(form);
        assert.strictEqual(form.$('.o_field_widget.o_priority').find('a.o_priority_star').length,2,
            "shouldstillhavetwostars");
        assert.strictEqual(form.$('.o_field_widget.o_priority').find('a.o_priority_star.fa-star').length,1,
            "shouldstillhaveonefullstarsincethevalueisthesecondvalue");
        assert.strictEqual(form.$('.o_field_widget.o_priority').find('a.o_priority_star.fa-star-o').length,1,
            "shouldstillhaveoneemptystarsincethevalueisthesecondvalue");

        //save
        awaittestUtils.form.clickSave(form);
        assert.strictEqual(form.$('.o_field_widget.o_priority').find('a.o_priority_star').length,2,
            "shouldstillhavetwostars");
        assert.strictEqual(form.$('.o_field_widget.o_priority').find('a.o_priority_star.fa-star').length,1,
            "shouldstillhaveonefullstarsincethevalueisthesecondvalue");
        assert.strictEqual(form.$('.o_field_widget.o_priority').find('a.o_priority_star.fa-star-o').length,1,
            "shouldstillhaveoneemptystarsincethevalueisthesecondvalue");

        //switchtoeditmodetocheckthatthenewvaluewasproperlywritten
        awaittestUtils.form.clickEdit(form);
        assert.strictEqual(form.$('.o_field_widget.o_priority').find('a.o_priority_star').length,2,
            "shouldstillhavetwostars");
        assert.strictEqual(form.$('.o_field_widget.o_priority').find('a.o_priority_star.fa-star').length,1,
            "shouldstillhaveonefullstarsincethevalueisthesecondvalue");
        assert.strictEqual(form.$('.o_field_widget.o_priority').find('a.o_priority_star.fa-star-o').length,1,
            "shouldstillhaveoneemptystarsincethevalueisthesecondvalue");

        //clickonthesecondstarineditmode
        awaittestUtils.dom.click(form.$('.o_field_widget.o_prioritya.o_priority_star.fa-star-o').last());

        assert.strictEqual(form.$('.o_field_widget.o_priority').find('a.o_priority_star').length,2,
            "shouldstillhavetwostars");
        assert.strictEqual(form.$('.o_field_widget.o_priority').find('a.o_priority_star.fa-star').length,2,
            "shouldnowhavetwofullstarssincethevalueisthethirdvalue");
        assert.strictEqual(form.$('.o_field_widget.o_priority').find('a.o_priority_star.fa-star-o').length,0,
            "shouldnowhavenoemptystarsincethevalueisthethirdvalue");

        //save
        awaittestUtils.form.clickSave(form);
        assert.strictEqual(form.$('.o_field_widget.o_priority').find('a.o_priority_star').length,2,
            "shouldstillhavetwostars");
        assert.strictEqual(form.$('.o_field_widget.o_priority').find('a.o_priority_star.fa-star').length,2,
            "shouldnowhavetwofullstarssincethevalueisthethirdvalue");
        assert.strictEqual(form.$('.o_field_widget.o_priority').find('a.o_priority_star.fa-star-o').length,0,
            "shouldnowhavenoemptystarsincethevalueisthethirdvalue");

        form.destroy();
    });

    QUnit.test('prioritywidgetineditablelistview',asyncfunction(assert){
        assert.expect(25);

        varlist=awaitcreateView({
            View:ListView,
            model:'partner',
            data:this.data,
            arch:'<treeeditable="bottom"><fieldname="selection"widget="priority"/></tree>',
        });

        assert.strictEqual(list.$('.o_data_row').first().find('.o_priority:not(.o_field_empty)').length,1,
            "widgetshouldbeconsideredset");
        assert.strictEqual(list.$('.o_data_row').first().find('.o_prioritya.o_priority_star').length,2,
            "shouldhavetwostarsforrepresentingeachpossiblevalue:nostar,onestarandtwostars");
        assert.strictEqual(list.$('.o_data_row').first().find('.o_prioritya.o_priority_star.fa-star').length,1,
            "shouldhaveonefullstarsincethevalueisthesecondvalue");
        assert.strictEqual(list.$('.o_data_row').first().find('.o_prioritya.o_priority_star.fa-star-o').length,1,
            "shouldhaveoneemptystarsincethevalueisthesecondvalue");

        //Hereweshouldtestwithmouseout,butcurrentlytheeffectassociatedwithit
        //occursinasetTimeoutafter200mssoit'snottrivialtotestithere.

        //switchtoeditmodeandchecktheresult
        var$cell=list.$('tbodytd:not(.o_list_record_selector)').first();
        awaittestUtils.dom.click($cell);
        assert.strictEqual(list.$('.o_data_row').first().find('.o_prioritya.o_priority_star').length,2,
            "shouldhavetwostarsforrepresentingeachpossiblevalue:nostar,onestarandtwostars");
        assert.strictEqual(list.$('.o_data_row').first().find('.o_prioritya.o_priority_star.fa-star').length,1,
            "shouldhaveonefullstarsincethevalueisthesecondvalue");
        assert.strictEqual(list.$('.o_data_row').first().find('.o_prioritya.o_priority_star.fa-star-o').length,1,
            "shouldhaveoneemptystarsincethevalueisthesecondvalue");

        //save
        awaittestUtils.dom.click(list.$buttons.find('.o_list_button_save'));
        assert.strictEqual(list.$('.o_data_row').first().find('.o_prioritya.o_priority_star').length,2,
            "shouldhavetwostarsforrepresentingeachpossiblevalue:nostar,onestarandtwostars");
        assert.strictEqual(list.$('.o_data_row').first().find('.o_prioritya.o_priority_star.fa-star').length,1,
            "shouldhaveonefullstarsincethevalueisthesecondvalue");
        assert.strictEqual(list.$('.o_data_row').first().find('.o_prioritya.o_priority_star.fa-star-o').length,1,
            "shouldhaveoneemptystarsincethevalueisthesecondvalue");

        //hoverlaststar
        list.$('.o_data_row.o_prioritya.o_priority_star.fa-star-o').first().trigger('mouseenter');
        assert.strictEqual(list.$('.o_data_row').first().find('.o_prioritya.o_priority_star').length,2,
            "shouldhavetwostarsforrepresentingeachpossiblevalue:nostar,onestarandtwostars");
        assert.strictEqual(list.$('.o_data_row').first().find('a.o_priority_star.fa-star').length,2,
            "shouldtemporaryhavetwofullstarssincewearehoveringthethirdvalue");
        assert.strictEqual(list.$('.o_data_row').first().find('a.o_priority_star.fa-star-o').length,0,
            "shouldtemporaryhavenoemptystarsincewearehoveringthethirdvalue");

        //clickonthefirststarinreadonlymode
        awaittestUtils.dom.click(list.$('.o_prioritya.o_priority_star.fa-star').first());

        assert.strictEqual(list.$('.o_data_row').first().find('.o_prioritya.o_priority_star').length,2,
            "shouldstillhavetwostars");
        assert.strictEqual(list.$('.o_data_row').first().find('.o_prioritya.o_priority_star.fa-star').length,0,
            "shouldnowhavenofullstarsincethevalueisthefirstvalue");
        assert.strictEqual(list.$('.o_data_row').first().find('.o_prioritya.o_priority_star.fa-star-o').length,2,
            "shouldnowhavetwoemptystarssincethevalueisthefirstvalue");

        //re-entereditmodetoforcere-renderingthewidgettocheckifthevaluewascorrectlysaved
        $cell=list.$('tbodytd:not(.o_list_record_selector)').first();
        awaittestUtils.dom.click($cell);

        assert.strictEqual(list.$('.o_data_row').first().find('.o_prioritya.o_priority_star').length,2,
            "shouldstillhavetwostars");
        assert.strictEqual(list.$('.o_data_row').first().find('.o_prioritya.o_priority_star.fa-star').length,0,
            "shouldnowonlyhavenofullstarsincethevalueisthefirstvalue");
        assert.strictEqual(list.$('.o_data_row').first().find('.o_prioritya.o_priority_star.fa-star-o').length,2,
            "shouldnowhavetwoemptystarssincethevalueisthefirstvalue");

        //Clickonsecondstarineditmode
        awaittestUtils.dom.click(list.$('.o_prioritya.o_priority_star.fa-star-o').last());

        assert.strictEqual(list.$('.o_data_row').last().find('.o_prioritya.o_priority_star').length,2,
            "shouldstillhavetwostars");
        assert.strictEqual(list.$('.o_data_row').last().find('.o_prioritya.o_priority_star.fa-star').length,2,
            "shouldnowhavetwofullstarssincethevalueisthethirdvalue");
        assert.strictEqual(list.$('.o_data_row').last().find('.o_prioritya.o_priority_star.fa-star-o').length,0,
            "shouldnowhavenoemptystarsincethevalueisthethirdvalue");

        //save
        awaittestUtils.dom.click(list.$buttons.find('.o_list_button_save'));
        assert.strictEqual(list.$('.o_data_row').last().find('.o_prioritya.o_priority_star').length,2,
            "shouldstillhavetwostars");
        assert.strictEqual(list.$('.o_data_row').last().find('.o_prioritya.o_priority_star.fa-star').length,2,
            "shouldnowhavetwofullstarssincethevalueisthethirdvalue");
        assert.strictEqual(list.$('.o_data_row').last().find('.o_prioritya.o_priority_star.fa-star-o').length,0,
            "shouldnowhavenoemptystarsincethevalueisthethirdvalue");

        list.destroy();
    });

    QUnit.test('prioritywidgetwithreadonlyattribute',asyncfunction(assert){
        assert.expect(1);

        constform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:`
                <form>
                    <fieldname="selection"widget="priority"readonly="1"/>
                </form>`,
            res_id:2,
        });

        assert.containsN(form,'.o_field_widget.o_priorityspan',2,
            "starsofprioritywidgetshouldrenderedwithspantagifreadonly");

        form.destroy();
    });

    QUnit.module('StateSelectionWidget');

    QUnit.test('state_selectionwidgetinformview',asyncfunction(assert){
        assert.expect(21);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<sheet>'+
                        '<group>'+
                            '<fieldname="selection"widget="state_selection"/>'+
                        '</group>'+
                    '</sheet>'+
                '</form>',
            res_id:1,
            viewOptions:{
                disable_autofocus:true,
            },
        });

        assert.containsOnce(form,'.o_field_widget.o_selection>aspan.o_status.o_status_red',
            "shouldhaveoneredstatussinceselectionisthesecond,blockedstate");
        assert.containsNone(form,'.o_field_widget.o_selection>aspan.o_status.o_status_green',
            "shouldnothaveonegreenstatussinceselectionisthesecond,blockedstate");
        assert.containsNone(form,'.dropdown-menu.state:visible',
            "thereshouldnotbeadropdown");

        //Clickonthestatusbuttontomakethedropdownappear
        awaittestUtils.dom.click(form.$('.o_field_widget.o_selection.o_status').first());
        assert.containsOnce(form,'.dropdown-menu.state:visible',
            "thereshouldbeadropdown");
        assert.containsN(form,'.dropdown-menu.state:visible.dropdown-item',2,
            "thereshouldbetwooptionsinthedropdown");

        //Clickonthefirstoption,"Normal"
        awaittestUtils.dom.click(form.$('.dropdown-menu.state:visible.dropdown-item').first());
        assert.containsNone(form,'.dropdown-menu.state:visible',
            "thereshouldnotbeadropdownanymore");
        assert.containsNone(form,'.o_field_widget.o_selection>aspan.o_status.o_status_red',
            "shouldnothaveoneredstatussinceselectionisthefirst,normalstate");
        assert.containsNone(form,'.o_field_widget.o_selection>aspan.o_status.o_status_green',
            "shouldnothaveonegreenstatussinceselectionisthefirst,normalstate");
        assert.containsOnce(form,'.o_field_widget.o_selection>aspan.o_status',
            "shouldhaveonegreystatussinceselectionisthefirst,normalstate");

        //switchtoeditmodeandchecktheresult
        awaittestUtils.form.clickEdit(form);
        assert.containsNone(form,'.dropdown-menu.state:visible',
            "thereshouldstillnotbeadropdown");
        assert.containsNone(form,'.o_field_widget.o_selection>aspan.o_status.o_status_red',
            "shouldstillnothaveoneredstatussinceselectionisthefirst,normalstate");
        assert.containsNone(form,'.o_field_widget.o_selection>aspan.o_status.o_status_green',
            "shouldstillnothaveonegreenstatussinceselectionisthefirst,normalstate");
        assert.containsOnce(form,'.o_field_widget.o_selection>aspan.o_status',
            "shouldstillhaveonegreystatussinceselectionisthefirst,normalstate");

        //Clickonthestatusbuttontomakethedropdownappear
        awaittestUtils.dom.click(form.$('.o_field_widget.o_selection.o_status').first());
        assert.containsOnce(form,'.dropdown-menu.state:visible',
            "thereshouldbeadropdown");
        assert.containsN(form,'.dropdown-menu.state:visible.dropdown-item',2,
            "thereshouldbetwooptionsinthedropdown");

        //Clickonthelastoption,"Done"
        awaittestUtils.dom.click(form.$('.dropdown-menu.state:visible.dropdown-item').last());
        assert.containsNone(form,'.dropdown-menu.state:visible',
            "thereshouldnotbeadropdownanymore");
        assert.containsNone(form,'.o_field_widget.o_selection>aspan.o_status.o_status_red',
            "shouldnothaveoneredstatussinceselectionisthethird,donestate");
        assert.containsOnce(form,'.o_field_widget.o_selection>aspan.o_status.o_status_green',
            "shouldhaveonegreenstatussinceselectionisthethird,donestate");

        //save
        awaittestUtils.form.clickSave(form);
        assert.containsNone(form,'.dropdown-menu.state:visible',
            "thereshouldstillnotbeadropdownanymore");
        assert.containsNone(form,'.o_field_widget.o_selection>aspan.o_status.o_status_red',
            "shouldstillnothaveoneredstatussinceselectionisthethird,donestate");
        assert.containsOnce(form,'.o_field_widget.o_selection>aspan.o_status.o_status_green',
            "shouldstillhaveonegreenstatussinceselectionisthethird,donestate");

        form.destroy();
    });

    QUnit.test('state_selectionwidgetwithreadonlymodifier',asyncfunction(assert){
        assert.expect(4);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<form><fieldname="selection"widget="state_selection"readonly="1"/></form>',
            res_id:1,
        });

        assert.hasClass(form.$('.o_selection'),'o_readonly_modifier');
        assert.hasClass(form.$('.o_selection>a'),'disabled');
        assert.isNotVisible(form.$('.dropdown-menu.state'));

        awaittestUtils.dom.click(form.$('.o_selection>a'));
        assert.isNotVisible(form.$('.dropdown-menu.state'));

        form.destroy();
    });

    QUnit.test('state_selectionwidgetineditablelistview',asyncfunction(assert){
        assert.expect(32);

        varlist=awaitcreateView({
            View:ListView,
            model:'partner',
            data:this.data,
            arch:'<treeeditable="bottom">'+
                    '<fieldname="foo"/>'+
                    '<fieldname="selection"widget="state_selection"/>'+
                  '</tree>',
        });

        assert.containsN(list,'.o_state_selection_cell.o_selection>aspan.o_status',5,
            "shouldhavefivestatusselectionwidgets");
        assert.containsOnce(list,'.o_state_selection_cell.o_selection>aspan.o_status.o_status_red',
            "shouldhaveoneredstatus");
        assert.containsOnce(list,'.o_state_selection_cell.o_selection>aspan.o_status.o_status_green',
            "shouldhaveonegreenstatus");
        assert.containsNone(list,'.dropdown-menu.state:visible',
            "thereshouldnotbeadropdown");

        //Clickonthestatusbuttontomakethedropdownappear
        var$cell=list.$('tbodytd.o_state_selection_cell').first();
        awaittestUtils.dom.click(list.$('.o_state_selection_cell.o_selection>aspan.o_status').first());
        assert.doesNotHaveClass($cell.parent(),'o_selected_row',
            'shouldnotbeineditmodesinceweclickedonthestateselectionwidget');
        assert.containsOnce(list,'.dropdown-menu.state:visible',
            "thereshouldbeadropdown");
        assert.containsN(list,'.dropdown-menu.state:visible.dropdown-item',2,
            "thereshouldbetwooptionsinthedropdown");

        //Clickonthefirstoption,"Normal"
        awaittestUtils.dom.click(list.$('.dropdown-menu.state:visible.dropdown-item').first());
        assert.containsN(list,'.o_state_selection_cell.o_selection>aspan.o_status',5,
            "shouldstillhavefivestatusselectionwidgets");
        assert.containsNone(list,'.o_state_selection_cell.o_selection>aspan.o_status.o_status_red',
            "shouldnowhavenoredstatus");
        assert.containsOnce(list,'.o_state_selection_cell.o_selection>aspan.o_status.o_status_green',
            "shouldstillhaveonegreenstatus");
        assert.containsNone(list,'.dropdown-menu.state:visible',
            "thereshouldnotbeadropdown");

        //switchtoeditmodeandchecktheresult
        $cell=list.$('tbodytd.o_state_selection_cell').first();
        awaittestUtils.dom.click($cell);
        assert.hasClass($cell.parent(),'o_selected_row',
            'shouldnowbeineditmode');
        assert.containsN(list,'.o_state_selection_cell.o_selection>aspan.o_status',5,
            "shouldstillhavefivestatusselectionwidgets");
        assert.containsNone(list,'.o_state_selection_cell.o_selection>aspan.o_status.o_status_red',
            "shouldnowhavenoredstatus");
        assert.containsOnce(list,'.o_state_selection_cell.o_selection>aspan.o_status.o_status_green',
            "shouldstillhaveonegreenstatus");
        assert.containsNone(list,'.dropdown-menu.state:visible',
            "thereshouldnotbeadropdown");

        //Clickonthestatusbuttontomakethedropdownappear
        awaittestUtils.dom.click(list.$('.o_state_selection_cell.o_selection>aspan.o_status').first());
        assert.containsOnce(list,'.dropdown-menu.state:visible',
            "thereshouldbeadropdown");
        assert.containsN(list,'.dropdown-menu.state:visible.dropdown-item',2,
            "thereshouldbetwooptionsinthedropdown");

        //Clickonanotherrow
        var$lastCell=list.$('tbodytd.o_state_selection_cell').last();
        awaittestUtils.dom.click($lastCell);
        assert.containsNone(list,'.dropdown-menu.state:visible',
            "thereshouldnotbeadropdownanymore");
        var$firstCell=list.$('tbodytd.o_state_selection_cell').first();
        assert.doesNotHaveClass($firstCell.parent(),'o_selected_row',
            'firstrowshouldnotbeineditmodeanymore');
        assert.hasClass($lastCell.parent(),'o_selected_row',
            'lastrowshouldbeineditmode');

        //Clickonthelaststatusbuttontomakethedropdownappear
        awaittestUtils.dom.click(list.$('.o_state_selection_cell.o_selection>aspan.o_status').last());
        assert.containsOnce(list,'.dropdown-menu.state:visible',
            "thereshouldbeadropdown");
        assert.containsN(list,'.dropdown-menu.state:visible.dropdown-item',2,
            "thereshouldbetwooptionsinthedropdown");

        //Clickonthelastoption,"Done"
        awaittestUtils.dom.click(list.$('.dropdown-menu.state:visible.dropdown-item').last());
        assert.containsNone(list,'.dropdown-menu.state:visible',
            "thereshouldnotbeadropdownanymore");
        assert.containsN(list,'.o_state_selection_cell.o_selection>aspan.o_status',5,
            "shouldstillhavefivestatusselectionwidgets");
        assert.containsNone(list,'.o_state_selection_cell.o_selection>aspan.o_status.o_status_red',
            "shouldstillhavenoredstatus");
        assert.containsN(list,'.o_state_selection_cell.o_selection>aspan.o_status.o_status_green',2,
            "shouldnowhavetwogreenstatus");
        assert.containsNone(list,'.dropdown-menu.state:visible',
            "thereshouldnotbeadropdown");

        //save
        awaittestUtils.dom.click(list.$buttons.find('.o_list_button_save'));
        assert.containsN(list,'.o_state_selection_cell.o_selection>aspan.o_status',5,
            "shouldhavefivestatusselectionwidgets");
        assert.containsNone(list,'.o_state_selection_cell.o_selection>aspan.o_status.o_status_red',
            "shouldhavenoredstatus");
        assert.containsN(list,'.o_state_selection_cell.o_selection>aspan.o_status.o_status_green',2,
            "shouldhavetwogreenstatus");
        assert.containsNone(list,'.dropdown-menu.state:visible',
            "thereshouldnotbeadropdown");

        list.destroy();
    });


    QUnit.module('FavoriteWidget');

    QUnit.test('favoritewidgetinkanbanview',asyncfunction(assert){
        assert.expect(4);

        varkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:'<kanbanclass="o_kanban_test">'+
                    '<templates>'+
                        '<tt-name="kanban-box">'+
                            '<div>'+
                                '<fieldname="bar"widget="boolean_favorite"/>'+
                            '</div>'+
                        '</t>'+
                    '</templates>'+
                  '</kanban>',
            domain:[['id','=',1]],
        });

        assert.containsOnce(kanban,'.o_kanban_record.o_field_widget.o_favorite>ai.fa.fa-star',
            'shouldbefavorite');
        assert.strictEqual(kanban.$('.o_kanban_record.o_field_widget.o_favorite>a').text(),'RemovefromFavorites',
            'thelabelshouldsay"RemovefromFavorites"');

        //clickonfavorite
        awaittestUtils.dom.click(kanban.$('.o_field_widget.o_favorite'));
        assert.containsNone(kanban,'.o_kanban_record .o_field_widget.o_favorite>ai.fa.fa-star',
            'shouldnotbefavorite');
        assert.strictEqual(kanban.$('.o_kanban_record .o_field_widget.o_favorite>a').text(),'AddtoFavorites',
            'thelabelshouldsay"AddtoFavorites"');

        kanban.destroy();
    });

    QUnit.test('favoritewidgetinformview',asyncfunction(assert){
        assert.expect(10);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<sheet>'+
                        '<group>'+
                            '<fieldname="bar"widget="boolean_favorite"/>'+
                        '</group>'+
                    '</sheet>'+
                '</form>',
            res_id:1,
        });

        assert.containsOnce(form,'.o_field_widget.o_favorite>ai.fa.fa-star',
            'shouldbefavorite');
        assert.strictEqual(form.$('.o_field_widget.o_favorite>a').text(),'RemovefromFavorites',
            'thelabelshouldsay"RemovefromFavorites"');

        //clickonfavorite
        awaittestUtils.dom.click(form.$('.o_field_widget.o_favorite'));
        assert.containsNone(form,'.o_field_widget.o_favorite>ai.fa.fa-star',
            'shouldnotbefavorite');
        assert.strictEqual(form.$('.o_field_widget.o_favorite>a').text(),'AddtoFavorites',
            'thelabelshouldsay"AddtoFavorites"');

        //switchtoeditmode
        awaittestUtils.form.clickEdit(form);
        assert.containsOnce(form,'.o_field_widget.o_favorite>ai.fa.fa-star-o',
            'shouldnotbefavorite');
        assert.strictEqual(form.$('.o_field_widget.o_favorite>a').text(),'AddtoFavorites',
            'thelabelshouldsay"AddtoFavorites"');

        //clickonfavorite
        awaittestUtils.dom.click(form.$('.o_field_widget.o_favorite'));
        assert.containsOnce(form,'.o_field_widget.o_favorite>ai.fa.fa-star',
            'shouldbefavorite');
        assert.strictEqual(form.$('.o_field_widget.o_favorite>a').text(),'RemovefromFavorites',
            'thelabelshouldsay"RemovefromFavorites"');

        //save
        awaittestUtils.form.clickSave(form);
        assert.containsOnce(form,'.o_field_widget.o_favorite>ai.fa.fa-star',
            'shouldbefavorite');
        assert.strictEqual(form.$('.o_field_widget.o_favorite>a').text(),'RemovefromFavorites',
            'thelabelshouldsay"RemovefromFavorites"');

        form.destroy();
    });

    QUnit.test('favoritewidgetineditablelistviewwithoutlabel',asyncfunction(assert){
        assert.expect(4);

        varlist=awaitcreateView({
            View:ListView,
            model:'partner',
            data:this.data,
            arch:'<treeeditable="bottom">'+
                    '<fieldname="bar"widget="boolean_favorite"nolabel="1"/>'+
                  '</tree>',
        });

        assert.containsOnce(list,'.o_data_row:first.o_field_widget.o_favorite>ai.fa.fa-star',
            'shouldbefavorite');

        //switchtoeditmode
        awaittestUtils.dom.click(list.$('tbodytd:not(.o_list_record_selector)').first());
        assert.containsOnce(list,'.o_data_row:first.o_field_widget.o_favorite>ai.fa.fa-star',
            'shouldbefavorite');

        //clickonfavorite
        awaittestUtils.dom.click(list.$('.o_data_row:first.o_field_widget.o_favorite'));
        assert.containsNone(list,'.o_data_row:first.o_field_widget.o_favorite>ai.fa.fa-star',
            'shouldnotbefavorite');

        //save
        awaittestUtils.dom.click(list.$buttons.find('.o_list_button_save'));
        assert.containsOnce(list,'.o_data_row:first.o_field_widget.o_favorite>ai.fa.fa-star-o',
            'shouldnotbefavorite');

        list.destroy();
    });


    QUnit.module('LabelSelectionWidget');

    QUnit.test('label_selectionwidgetinformview',asyncfunction(assert){
        assert.expect(12);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<sheet>'+
                        '<group>'+
                            '<fieldname="selection"widget="label_selection"'+
                            'options="{\'classes\':{\'normal\':\'secondary\',\'blocked\':\'warning\',\'done\':\'success\'}}"/>'+
                        '</group>'+
                    '</sheet>'+
                '</form>',
            res_id:1,
        });

        assert.containsOnce(form,'.o_field_widget.badge.badge-warning',
            "shouldhaveawarningstatuslabelsinceselectionisthesecond,blockedstate");
        assert.containsNone(form,'.o_field_widget.badge.badge-secondary',
            "shouldnothaveadefaultstatussinceselectionisthesecond,blockedstate");
        assert.containsNone(form,'.o_field_widget.badge.badge-success',
            "shouldnothaveasuccessstatussinceselectionisthesecond,blockedstate");
        assert.strictEqual(form.$('.o_field_widget.badge.badge-warning').text(),'Blocked',
            "thelabelshouldsay'Blocked'sincethisisthelabelvalueforthatstate");

        ////switchtoeditmodeandchecktheresult
        awaittestUtils.form.clickEdit(form);
        assert.containsOnce(form,'.o_field_widget.badge.badge-warning',
            "shouldhaveawarningstatuslabelsinceselectionisthesecond,blockedstate");
        assert.containsNone(form,'.o_field_widget.badge.badge-secondary',
            "shouldnothaveadefaultstatussinceselectionisthesecond,blockedstate");
        assert.containsNone(form,'.o_field_widget.badge.badge-success',
            "shouldnothaveasuccessstatussinceselectionisthesecond,blockedstate");
        assert.strictEqual(form.$('.o_field_widget.badge.badge-warning').text(),'Blocked',
            "thelabelshouldsay'Blocked'sincethisisthelabelvalueforthatstate");

        //save
        awaittestUtils.form.clickSave(form);
        assert.containsOnce(form,'.o_field_widget.badge.badge-warning',
            "shouldhaveawarningstatuslabelsinceselectionisthesecond,blockedstate");
        assert.containsNone(form,'.o_field_widget.badge.badge-secondary',
            "shouldnothaveadefaultstatussinceselectionisthesecond,blockedstate");
        assert.containsNone(form,'.o_field_widget.badge.badge-success',
            "shouldnothaveasuccessstatussinceselectionisthesecond,blockedstate");
        assert.strictEqual(form.$('.o_field_widget.badge.badge-warning').text(),'Blocked',
            "thelabelshouldsay'Blocked'sincethisisthelabelvalueforthatstate");

        form.destroy();
    });

    QUnit.test('label_selectionwidgetineditablelistview',asyncfunction(assert){
        assert.expect(21);

        varlist=awaitcreateView({
            View:ListView,
            model:'partner',
            data:this.data,
            arch:'<treeeditable="bottom">'+
                    '<fieldname="foo"/>'+
                    '<fieldname="selection"widget="label_selection"'+
                    'options="{\'classes\':{\'normal\':\'secondary\',\'blocked\':\'warning\',\'done\':\'success\'}}"/>'+
                  '</tree>',
        });

        assert.strictEqual(list.$('.o_field_widget.badge:not(:empty)').length,3,
            "shouldhavethreevisiblestatuslabels");
        assert.containsOnce(list,'.o_field_widget.badge.badge-warning',
            "shouldhaveonewarningstatuslabel");
        assert.strictEqual(list.$('.o_field_widget.badge.badge-warning').text(),'Blocked',
            "thewarninglabelshouldread'Blocked'");
        assert.containsOnce(list,'.o_field_widget.badge.badge-secondary',
            "shouldhaveonedefaultstatuslabel");
        assert.strictEqual(list.$('.o_field_widget.badge.badge-secondary').text(),'Normal',
            "thedefaultlabelshouldread'Normal'");
        assert.containsOnce(list,'.o_field_widget.badge.badge-success',
            "shouldhaveonesuccessstatuslabel");
        assert.strictEqual(list.$('.o_field_widget.badge.badge-success').text(),'Done',
            "thesuccesslabelshouldread'Done'");

        //switchtoeditmodeandchecktheresult
        awaittestUtils.dom.clickFirst(list.$('tbodytd:not(.o_list_record_selector)'));
        assert.strictEqual(list.$('.o_field_widget.badge:not(:empty)').length,3,
            "shouldhavethreevisiblestatuslabels");
        assert.containsOnce(list,'.o_field_widget.badge.badge-warning',
            "shouldhaveonewarningstatuslabel");
        assert.strictEqual(list.$('.o_field_widget.badge.badge-warning').text(),'Blocked',
            "thewarninglabelshouldread'Blocked'");
        assert.containsOnce(list,'.o_field_widget.badge.badge-secondary',
            "shouldhaveonedefaultstatuslabel");
        assert.strictEqual(list.$('.o_field_widget.badge.badge-secondary').text(),'Normal',
            "thedefaultlabelshouldread'Normal'");
        assert.containsOnce(list,'.o_field_widget.badge.badge-success',
            "shouldhaveonesuccessstatuslabel");
        assert.strictEqual(list.$('.o_field_widget.badge.badge-success').text(),'Done',
            "thesuccesslabelshouldread'Done'");

        //saveandchecktheresult
        awaittestUtils.dom.click(list.$buttons.find('.o_list_button_save'));
        assert.strictEqual(list.$('.o_field_widget.badge:not(:empty)').length,3,
            "shouldhavethreevisiblestatuslabels");
        assert.containsOnce(list,'.o_field_widget.badge.badge-warning',
            "shouldhaveonewarningstatuslabel");
        assert.strictEqual(list.$('.o_field_widget.badge.badge-warning').text(),'Blocked',
            "thewarninglabelshouldread'Blocked'");
        assert.containsOnce(list,'.o_field_widget.badge.badge-secondary',
            "shouldhaveonedefaultstatuslabel");
        assert.strictEqual(list.$('.o_field_widget.badge.badge-secondary').text(),'Normal',
            "thedefaultlabelshouldread'Normal'");
        assert.containsOnce(list,'.o_field_widget.badge.badge-success',
            "shouldhaveonesuccessstatuslabel");
        assert.strictEqual(list.$('.o_field_widget.badge.badge-success').text(),'Done',
            "thesuccesslabelshouldread'Done'");

        list.destroy();
    });


    QUnit.module('StatInfo');

    QUnit.test('statinfowidgetformatsdecimalprecision',asyncfunction(assert){
        //sometimestheroundmethodcanreturnnumberssuchas14.000001
        //whenaskedtoroundanumberto2decimals,assuchisthebehaviouroffloats.
        //wecheckthateveninthateventuality,onlytwodecimalsaredisplayed
        assert.expect(2);

        this.data.partner.fields.monetary={string:"Monetary",type:'monetary'};
        this.data.partner.records[0].monetary=9.999999;
        this.data.partner.records[0].currency_id=1;

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                        '<buttonclass="oe_stat_button"name="items"icon="fa-gear">'+
                            '<fieldname="qux"widget="statinfo"/>'+
                        '</button>'+
                        '<buttonclass="oe_stat_button"name="money"icon="fa-money">'+
                            '<fieldname="monetary"widget="statinfo"/>'+
                        '</button>'+
                  '</form>',
            res_id:1,
        });

        //formatFloatrendersaccordingtothis.field.digits
        assert.strictEqual(form.$('.oe_stat_button.o_field_widget.o_stat_info.o_stat_value').eq(0).text(),
            '0.4',"Defaultprecisionshouldbe[16,1]");
        assert.strictEqual(form.$('.oe_stat_button.o_field_widget.o_stat_info.o_stat_value').eq(1).text(),
            '10.00',"Currencydecimalprecisionshouldbe2");

        form.destroy();
    });

    QUnit.test('statinfowidgetinformview',asyncfunction(assert){
        assert.expect(9);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<sheet>'+
                        '<divclass="oe_button_box"name="button_box">'+
                            '<buttonclass="oe_stat_button"name="items" type="object"icon="fa-gear">'+
                                '<fieldname="int_field"widget="statinfo"/>'+
                            '</button>'+
                        '</div>'+
                        '<group>'+
                            '<fieldname="foo"/>'+
                        '</group>'+
                    '</sheet>'+
                '</form>',
            res_id:1,
        });

        assert.containsOnce(form,'.oe_stat_button.o_field_widget.o_stat_info',
            "shouldhaveonestatbutton");
        assert.strictEqual(form.$('.oe_stat_button.o_field_widget.o_stat_info.o_stat_value').text(),
            '10',"shouldhave10asvalue");
        assert.strictEqual(form.$('.oe_stat_button.o_field_widget.o_stat_info.o_stat_text').text(),
            'int_field',"shouldhave'int_field'astext");

        //switchtoeditmodeandchecktheresult
        awaittestUtils.form.clickEdit(form);
        assert.containsOnce(form,'.oe_stat_button.o_field_widget.o_stat_info',
            "shouldstillhaveonestatbutton");
        assert.strictEqual(form.$('.oe_stat_button.o_field_widget.o_stat_info.o_stat_value').text(),
            '10',"shouldstillhave10asvalue");
        assert.strictEqual(form.$('.oe_stat_button.o_field_widget.o_stat_info.o_stat_text').text(),
            'int_field',"shouldhave'int_field'astext");

        //save
        awaittestUtils.form.clickSave(form);
        assert.containsOnce(form,'.oe_stat_button.o_field_widget.o_stat_info',
            "shouldhaveonestatbutton");
        assert.strictEqual(form.$('.oe_stat_button.o_field_widget.o_stat_info.o_stat_value').text(),
            '10',"shouldhave10asvalue");
        assert.strictEqual(form.$('.oe_stat_button.o_field_widget.o_stat_info.o_stat_text').text(),
            'int_field',"shouldhave'int_field'astext");

        form.destroy();
    });

    QUnit.test('statinfowidgetinformviewwithspecificlabel_field',asyncfunction(assert){
        assert.expect(9);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<sheet>'+
                        '<divclass="oe_button_box"name="button_box">'+
                            '<buttonclass="oe_stat_button"name="items" type="object"icon="fa-gear">'+
                                '<fieldstring="Usefulstatbutton"name="int_field"widget="statinfo"'+
                                        'options="{\'label_field\':\'foo\'}"/>'+
                            '</button>'+
                        '</div>'+
                        '<group>'+
                            '<fieldname="foo"invisible="1"/>'+
                            '<fieldname="bar"/>'+
                        '</group>'+
                    '</sheet>'+
                '</form>',
            res_id:1,
        });

        assert.containsOnce(form,'.oe_stat_button.o_field_widget.o_stat_info',
            "shouldhaveonestatbutton");
        assert.strictEqual(form.$('.oe_stat_button.o_field_widget.o_stat_info.o_stat_value').text(),
            '10',"shouldhave10asvalue");
        assert.strictEqual(form.$('.oe_stat_button.o_field_widget.o_stat_info.o_stat_text').text(),
            'yop',"shouldhave'yop'astext,sinceitisthevalueoffieldfoo");

        //switchtoeditmodeandchecktheresult
        awaittestUtils.form.clickEdit(form);
        assert.containsOnce(form,'.oe_stat_button.o_field_widget.o_stat_info',
            "shouldstillhaveonestatbutton");
        assert.strictEqual(form.$('.oe_stat_button.o_field_widget.o_stat_info.o_stat_value').text(),
            '10',"shouldstillhave10asvalue");
        assert.strictEqual(form.$('.oe_stat_button.o_field_widget.o_stat_info.o_stat_text').text(),
            'yop',"shouldhave'yop'astext,sinceitisthevalueoffieldfoo");

        //save
        awaittestUtils.form.clickSave(form);
        assert.containsOnce(form,'.oe_stat_button.o_field_widget.o_stat_info',
            "shouldhaveonestatbutton");
        assert.strictEqual(form.$('.oe_stat_button.o_field_widget.o_stat_info.o_stat_value').text(),
            '10',"shouldhave10asvalue");
        assert.strictEqual(form.$('.oe_stat_button.o_field_widget.o_stat_info.o_stat_text').text(),
            'yop',"shouldhave'yop'astext,sinceitisthevalueoffieldfoo");

        form.destroy();
    });

    QUnit.test('statinfowidgetinformviewwithnolabel',asyncfunction(assert){
        assert.expect(9);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<sheet>'+
                        '<divclass="oe_button_box"name="button_box">'+
                            '<buttonclass="oe_stat_button"name="items" type="object"icon="fa-gear">'+
                                '<fieldstring="Usefulstatbutton"name="int_field"widget="statinfo"nolabel="1"/>'+
                            '</button>'+
                        '</div>'+
                        '<group>'+
                            '<fieldname="foo"invisible="1"/>'+
                            '<fieldname="bar"/>'+
                        '</group>'+
                    '</sheet>'+
                '</form>',
            res_id:1,
        });

        assert.containsOnce(form,'.oe_stat_button.o_field_widget.o_stat_info',
            "shouldhaveonestatbutton");
        assert.strictEqual(form.$('.oe_stat_button.o_field_widget.o_stat_info.o_stat_value').text(),
            '10',"shouldhave10asvalue");
        assert.strictEqual(form.$('.oe_stat_button.o_field_widget.o_stat_info.o_stat_text').text(),
            '',"shouldnothaveanylabel");

        //switchtoeditmodeandchecktheresult
        awaittestUtils.form.clickEdit(form);
        assert.containsOnce(form,'.oe_stat_button.o_field_widget.o_stat_info',
            "shouldstillhaveonestatbutton");
        assert.strictEqual(form.$('.oe_stat_button.o_field_widget.o_stat_info.o_stat_value').text(),
            '10',"shouldstillhave10asvalue");
        assert.strictEqual(form.$('.oe_stat_button.o_field_widget.o_stat_info.o_stat_text').text(),
            '',"shouldnothaveanylabel");

        //save
        awaittestUtils.form.clickSave(form);
        assert.containsOnce(form,'.oe_stat_button.o_field_widget.o_stat_info',
            "shouldhaveonestatbutton");
        assert.strictEqual(form.$('.oe_stat_button.o_field_widget.o_stat_info.o_stat_value').text(),
            '10',"shouldhave10asvalue");
        assert.strictEqual(form.$('.oe_stat_button.o_field_widget.o_stat_info.o_stat_text').text(),
            '',"shouldnothaveanylabel");

        form.destroy();
    });


    QUnit.module('PercentPie');

    QUnit.test('percentpiewidgetinformviewwithvalue<50%',asyncfunction(assert){
        assert.expect(12);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<sheet>'+
                        '<group>'+
                            '<fieldname="int_field"widget="percentpie"/>'+
                        '</group>'+
                    '</sheet>'+
                '</form>',
            res_id:1,
        });

        assert.containsOnce(form,'.o_field_percent_pie.o_field_widget.o_pie',
            "shouldhaveapiechart");
        assert.strictEqual(form.$('.o_field_percent_pie.o_field_widget.o_pie.o_pie_value').text(),
            '10%',"shouldhave10%aspievaluesinceint_field=10");
        assert.ok(_.str.include(form.$('.o_field_percent_pie.o_field_widget.o_pie.o_mask').first().attr('style'),
            'transform:rotate(180deg);'),"leftmaskshouldbecoveringthewholeleftsideofthepie");
        assert.ok(_.str.include(form.$('.o_field_percent_pie.o_field_widget.o_pie.o_mask').last().attr('style'),
            'transform:rotate(36deg);'),"rightmaskshouldberotatedfrom360*(10/100)=36degrees");

        //switchtoeditmodeandchecktheresult
        awaittestUtils.form.clickEdit(form);
        assert.containsOnce(form,'.o_field_percent_pie.o_field_widget.o_pie',
            "shouldhaveapiechart");
        assert.strictEqual(form.$('.o_field_percent_pie.o_field_widget.o_pie.o_pie_value').text(),
            '10%',"shouldhave10%aspievaluesinceint_field=10");
        assert.ok(_.str.include(form.$('.o_field_percent_pie.o_field_widget.o_pie.o_mask').first().attr('style'),
            'transform:rotate(180deg);'),"leftmaskshouldbecoveringthewholeleftsideofthepie");
        assert.ok(_.str.include(form.$('.o_field_percent_pie.o_field_widget.o_pie.o_mask').last().attr('style'),
            'transform:rotate(36deg);'),"rightmaskshouldberotatedfrom360*(10/100)=36degrees");

        //save
        awaittestUtils.form.clickSave(form);
        assert.containsOnce(form,'.o_field_percent_pie.o_field_widget.o_pie',
            "shouldhaveapiechart");
        assert.strictEqual(form.$('.o_field_percent_pie.o_field_widget.o_pie.o_pie_value').text(),
            '10%',"shouldhave10%aspievaluesinceint_field=10");
        assert.ok(_.str.include(form.$('.o_field_percent_pie.o_field_widget.o_pie.o_mask').first().attr('style'),
            'transform:rotate(180deg);'),"leftmaskshouldbecoveringthewholeleftsideofthepie");
        assert.ok(_.str.include(form.$('.o_field_percent_pie.o_field_widget.o_pie.o_mask').last().attr('style'),
            'transform:rotate(36deg);'),"rightmaskshouldberotatedfrom360*(10/100)=36degrees");

        form.destroy();
    });

    QUnit.test('percentpiewidgetinformviewwithvalue>50%',asyncfunction(assert){
        assert.expect(12);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<sheet>'+
                        '<group>'+
                            '<fieldname="int_field"widget="percentpie"/>'+
                        '</group>'+
                    '</sheet>'+
                '</form>',
            res_id:3,
        });

        assert.containsOnce(form,'.o_field_percent_pie.o_field_widget.o_pie',
            "shouldhaveapiechart");
        assert.strictEqual(form.$('.o_field_percent_pie.o_field_widget.o_pie.o_pie_value').text(),
            '80%',"shouldhave80%aspievaluesinceint_field=80");
        assert.ok(_.str.include(form.$('.o_field_percent_pie.o_field_widget.o_pie.o_mask').first().attr('style'),
            'transform:rotate(288deg);'),"leftmaskshouldberotatedfrom360*(80/100)=288degrees");
        assert.hasClass(form.$('.o_field_percent_pie.o_field_widget.o_pie.o_mask').last(),'o_full',
            "rightmaskshouldbehiddensincethevalue>50%");

        //switchtoeditmodeandchecktheresult
        awaittestUtils.form.clickEdit(form);
        assert.containsOnce(form,'.o_field_percent_pie.o_field_widget.o_pie',
            "shouldhaveapiechart");
        assert.strictEqual(form.$('.o_field_percent_pie.o_field_widget.o_pie.o_pie_value').text(),
            '80%',"shouldhave80%aspievaluesinceint_field=80");
        assert.ok(_.str.include(form.$('.o_field_percent_pie.o_field_widget.o_pie.o_mask').first().attr('style'),
            'transform:rotate(288deg);'),"leftmaskshouldberotatedfrom360*(80/100)=288degrees");
        assert.hasClass(form.$('.o_field_percent_pie.o_field_widget.o_pie.o_mask').last(),'o_full',
            "rightmaskshouldbehiddensincethevalue>50%");

        //save
        awaittestUtils.form.clickSave(form);
        assert.containsOnce(form,'.o_field_percent_pie.o_field_widget.o_pie',
            "shouldhaveapiechart");
        assert.strictEqual(form.$('.o_field_percent_pie.o_field_widget.o_pie.o_pie_value').text(),
            '80%',"shouldhave80%aspievaluesinceint_field=80");
        assert.ok(_.str.include(form.$('.o_field_percent_pie.o_field_widget.o_pie.o_mask').first().attr('style'),
            'transform:rotate(288deg);'),"leftmaskshouldberotatedfrom360*(80/100)=288degrees");
        assert.hasClass(form.$('.o_field_percent_pie.o_field_widget.o_pie.o_mask').last(),'o_full',
            "rightmaskshouldbehiddensincethevalue>50%");

        form.destroy();
    });

    //TODO:Thistestwouldpasswithoutanyissuesincealltheclassesand
    //      customstyleattributesarecorrectlysetonthewidgetinlist
    //      view,butsincethescssitselfforthiswidgetcurrentlyonly
    //      appliesinsidetheformview,thewidgetisunusable.Thistestcan
    //      beuncommentedwhenwerefactorthescssfilessothatthiswidget
    //      stylesheetappliesinbothformandlistview.
    //QUnit.test('percentpiewidgetineditablelistview',asyncfunction(assert){
    //    assert.expect(10);
    //
    //    varlist=awaitcreateView({
    //        View:ListView,
    //        model:'partner',
    //        data:this.data,
    //        arch:'<treeeditable="bottom">'+
    //                '<fieldname="foo"/>'+
    //                '<fieldname="int_field"widget="percentpie"/>'+
    //              '</tree>',
    //    });
    //
    //    assert.containsN(list,'.o_field_percent_pie.o_pie',5,
    //        "shouldhavefivepiecharts");
    //    assert.strictEqual(list.$('.o_field_percent_pie:first.o_pie.o_pie_value').first().text(),
    //        '10%',"shouldhave10%aspievaluesinceint_field=10");
    //    assert.strictEqual(list.$('.o_field_percent_pie:first.o_pie.o_mask').first().attr('style'),
    //        'transform:rotate(180deg);',"leftmaskshouldbecoveringthewholeleftsideofthepie");
    //    assert.strictEqual(list.$('.o_field_percent_pie:first.o_pie.o_mask').last().attr('style'),
    //        'transform:rotate(36deg);',"rightmaskshouldberotatedfrom360*(10/100)=36degrees");
    //
    //    //switchtoeditmodeandchecktheresult
//   testUtils.dom.click(    list.$('tbodytd:not(.o_list_record_selector)').first());
    //    assert.strictEqual(list.$('.o_field_percent_pie:first.o_pie.o_pie_value').first().text(),
    //        '10%',"shouldhave10%aspievaluesinceint_field=10");
    //    assert.strictEqual(list.$('.o_field_percent_pie:first.o_pie.o_mask').first().attr('style'),
    //        'transform:rotate(180deg);',"leftmaskshouldbecoveringthewholerightsideofthepie");
    //    assert.strictEqual(list.$('.o_field_percent_pie:first.o_pie.o_mask').last().attr('style'),
    //        'transform:rotate(36deg);',"rightmaskshouldberotatedfrom360*(10/100)=36degrees");
    //
    //    //save
//   testUtils.dom.click(    list.$buttons.find('.o_list_button_save'));
    //    assert.strictEqual(list.$('.o_field_percent_pie:first.o_pie.o_pie_value').first().text(),
    //        '10%',"shouldhave10%aspievaluesinceint_field=10");
    //    assert.strictEqual(list.$('.o_field_percent_pie:first.o_pie.o_mask').first().attr('style'),
    //        'transform:rotate(180deg);',"leftmaskshouldbecoveringthewholerightsideofthepie");
    //    assert.strictEqual(list.$('.o_field_percent_pie:first.o_pie.o_mask').last().attr('style'),
    //        'transform:rotate(36deg);',"rightmaskshouldberotatedfrom360*(10/100)=36degrees");
    //
    //    list.destroy();
    //});


    QUnit.module('FieldDomain');

    QUnit.test('Thedomaineditorshouldnotcrashtheviewwhengivenadynamicfilter',asyncfunction(assert){
        //dynamicfilters(containingvariables,suchasuid,parentortoday)
        //arenothandledbythedomaineditor,butitshouldn'tcrashtheview
        assert.expect(1);

        this.data.partner.records[0].foo='[["int_field","=",uid]]';

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:
                '<form>'+
                    '<fieldname="foo"widget="domain"options="{\'model\':\'partner\'}"/>'+
                    '<fieldname="int_field"invisible="1"/>'+
                '</form>',
            res_id:1,
            session:{
                user_context:{uid:14},
            },
        });

        assert.strictEqual(form.$('.o_read_mode').text(),"Thisdomainisnotsupported.",
            "Thewidgetshouldnotcrashtheview,butgracefullyadmititsfailure.");
        form.destroy();
    });

    QUnit.test('basicdomainfieldusageisok',asyncfunction(assert){
        assert.expect(7);

        this.data.partner.records[0].foo="[]";

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:
                '<form>'+
                    '<sheet>'+
                        '<group>'+
                            '<fieldname="foo"widget="domain"options="{\'model\':\'partner_type\'}"/>'+
                        '</group>'+
                    '</sheet>'+
                '</form>',
            res_id:1,
        });
        awaittestUtils.form.clickEdit(form);

        //Asthedomainisempty,thereshouldbeabuttontoaddthefirst
        //domainpart
        var$domain=form.$(".o_field_domain");
        var$domainAddFirstNodeButton=$domain.find(".o_domain_add_first_node_button");
        assert.equal($domainAddFirstNodeButton.length,1,
            "thereshouldbeabuttontocreatefirstdomainelement");

        //Clickingonthebuttonshouldaddthe[["id","=","1"]]domain,so
        //thereshouldbeafieldselectorintheDOM
        awaittestUtils.dom.click($domainAddFirstNodeButton);
        var$fieldSelector=$domain.find(".o_field_selector");
        assert.equal($fieldSelector.length,1,
            "thereshouldbeafieldselector");

        //Focusingthefieldselectorinputshouldopenthefieldselector
        //popover
        awaittestUtils.dom.triggerEvents($fieldSelector,'focus');
        var$fieldSelectorPopover=$fieldSelector.find(".o_field_selector_popover");
        assert.ok($fieldSelectorPopover.is(":visible"),
            "fieldselectorpopovershouldbevisible");

        assert.containsOnce($fieldSelectorPopover,'.o_field_selector_searchinput',
            "fieldselectorpopovershouldcontainasearchinput");

        //Thepopovershouldcontainthelistofpartner_typefieldsandso
        //thereshouldbethe"Colorindex"field
        var$lis=$fieldSelectorPopover.find("li");
        var$colorIndex=$();
        $lis.each(function(){
            var$li=$(this);
            if($li.html().indexOf("Colorindex")>=0){
                $colorIndex=$li;
            }
        });
        assert.equal($colorIndex.length,1,
            "fieldselectorpopovershouldcontain'Colorindex'field");

        //Clickingonthisfieldshouldclosethepopover,thenchangingthe
        //associatedvalueshouldrevealonematchedrecord
        awaittestUtils.dom.click($colorIndex);
        awaittestUtils.fields.editAndTrigger($('.o_domain_leaf_value_input'),2,['change']);
        assert.equal($domain.find(".o_domain_show_selection_button").text().trim().substr(0,2),"1",
            "changingcolorvalueto2shouldrevealonlyonerecord");

        //Savingtheformviewshouldshowareadonlydomaincontainingthe
        //"color"field
        awaittestUtils.form.clickSave(form);
        $domain=form.$(".o_field_domain");
        assert.ok($domain.html().indexOf("Colorindex")>=0,
            "fieldselectorreadonlyvalueshouldnowcontain'Colorindex'");
        form.destroy();
    });

    QUnit.test('domainfieldiscorrectlyresetoneveryviewchange',asyncfunction(assert){
        assert.expect(7);

        this.data.partner.records[0].foo='[["id","=",1]]';
        this.data.partner.fields.bar.type="char";
        this.data.partner.records[0].bar="product";

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:
                '<form>'+
                    '<sheet>'+
                        '<group>'+
                            '<fieldname="bar"/>'+
                            '<fieldname="foo"widget="domain"options="{\'model\':\'bar\'}"/>'+
                        '</group>'+
                    '</sheet>'+
                '</form>',
            res_id:1,
        });
        awaittestUtils.form.clickEdit(form);

        //Asthedomainisequalto[["id","=",1]]thereshouldbeafield
        //selectortochangethis
        var$domain=form.$(".o_field_domain");
        var$fieldSelector=$domain.find(".o_field_selector");
        assert.equal($fieldSelector.length,1,
            "thereshouldbeafieldselector");

        //Focusingitsinputshouldopenthefieldselectorpopover
        awaittestUtils.dom.triggerEvents($fieldSelector,'focus');
        var$fieldSelectorPopover=$fieldSelector.find(".o_field_selector_popover");
        assert.ok($fieldSelectorPopover.is(":visible"),
            "fieldselectorpopovershouldbevisible");

        //Asthevalueofthe"bar"fieldis"product",thefieldselector
        //popovershouldcontainthelistof"product"fields
        var$lis=$fieldSelectorPopover.find("li");
        var$sampleLi=$();
        $lis.each(function(){
            var$li=$(this);
            if($li.html().indexOf("ProductName")>=0){
                $sampleLi=$li;
            }
        });
        assert.strictEqual($lis.length,1,
            "fieldselectorpopovershouldcontainonlyonefield");
        assert.strictEqual($sampleLi.length,1,
            "fieldselectorpopovershouldcontain'ProductName'field");

        //Nowchangethevalueofthe"bar"fieldto"partner_type"
        awaittestUtils.dom.click(form.$("input.o_field_widget"));
        awaittestUtils.fields.editInput(form.$("input.o_field_widget"),"partner_type");

        //Refocusingthefieldselectorinputshouldopenthepopoveragain
        $fieldSelector=form.$(".o_field_selector");
        $fieldSelector.trigger('focusin');
        $fieldSelectorPopover=$fieldSelector.find(".o_field_selector_popover");
        assert.ok($fieldSelectorPopover.is(":visible"),
            "fieldselectorpopovershouldbevisible");

        //Nowthelistoffieldsshouldbetheonesofthe"partner_type"model
        $lis=$fieldSelectorPopover.find("li");
        $sampleLi=$();
        $lis.each(function(){
            var$li=$(this);
            if($li.html().indexOf("Colorindex")>=0){
                $sampleLi=$li;
            }
        });
        assert.strictEqual($lis.length,2,
            "fieldselectorpopovershouldcontaintwofields");
        assert.strictEqual($sampleLi.length,1,
            "fieldselectorpopovershouldcontain'Colorindex'field");
        form.destroy();
    });

    QUnit.test('domainfieldcanberesetwithanewdomain(fromonchange)',asyncfunction(assert){
        assert.expect(2);

        this.data.partner.records[0].foo='[]';
        this.data.partner.onchanges={
            display_name:function(obj){
                obj.foo='[["id","=",1]]';
            },
        };

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:
                '<form>'+
                    '<fieldname="display_name"/>'+
                    '<fieldname="foo"widget="domain"options="{\'model\':\'partner\'}"/>'+
                '</form>',
            res_id:1,
            viewOptions:{
                mode:'edit',
            },
        });

        assert.equal(form.$('.o_domain_show_selection_button').text().trim(),'5record(s)',
            "thedomainbeingempty,thereshouldbe5records");

        //updatedisplay_nametotriggertheonchangeandresetfoo
        awaittestUtils.fields.editInput(form.$('.o_field_widget[name=display_name]'),'newvalue');

        assert.equal(form.$('.o_domain_show_selection_button').text().trim(),'1record(s)',
            "thedomainhaschanged,thereshouldbeonly1record");

        form.destroy();
    });

    QUnit.test('domainfield:handlefalsedomainas[]',asyncfunction(assert){
        assert.expect(3);

        this.data.partner.records[0].foo=false;
        this.data.partner.fields.bar.type="char";
        this.data.partner.records[0].bar="product";

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:
                '<form>'+
                    '<sheet>'+
                        '<group>'+
                            '<fieldname="bar"/>'+
                            '<fieldname="foo"widget="domain"options="{\'model\':\'bar\'}"/>'+
                        '</group>'+
                    '</sheet>'+
                '</form>',
            mockRPC:function(route,args){
                if(args.method==='search_count'){
                    assert.deepEqual(args.args[0],[],"shouldsendavaliddomain");
                }
                returnthis._super.apply(this,arguments);
            },
            res_id:1,
        });

        assert.strictEqual(form.$('.o_field_widget[name=foo]:not(.o_field_empty)').length,1,
            "thereshouldbeadomainfield,notconsideredempty");

        awaittestUtils.form.clickEdit(form);

        var$warning=form.$('.o_field_widget[name=foo].text-warning');
        assert.strictEqual($warning.length,0,"shouldnotdisplaythatthedomainisinvalid");

        form.destroy();
    });

    QUnit.test('basicdomainfield:showtheselection',asyncfunction(assert){
        assert.expect(2);

        this.data.partner.records[0].foo="[]";

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:
                '<form>'+
                    '<sheet>'+
                        '<group>'+
                            '<fieldname="foo"widget="domain"options="{\'model\':\'partner_type\'}"/>'+
                        '</group>'+
                    '</sheet>'+
                '</form>',
            archs:{
                'partner_type,false,list':'<tree><fieldname="display_name"/></tree>',
                'partner_type,false,search':'<search><fieldname="name"string="Name"/></search>',
            },
            res_id:1,
        });

        assert.equal(form.$(".o_domain_show_selection_button").text().trim().substr(0,2),"2",
            "selectionshouldcontain2records");

        //opentheselection
        awaittestUtils.dom.click(form.$(".o_domain_show_selection_button"));
        assert.strictEqual($('.modal.o_list_view.o_data_row').length,2,
            "shouldhaveopenalistviewwith2recordsinadialog");

        //clickonarecord->shouldnotopentherecord
        //wedon'tactuallycheckthatitdoesn'topentherecordbecauseeven
        //ifittriesto,itwillcrashaswedon'tdefineanarchinthistest
        awaittestUtils.dom.click($('.modal.o_list_view.o_data_row:first.o_data_cell'));

        form.destroy();
    });

    QUnit.test('fieldcontextispropagatedwhenopeningselection',asyncfunction(assert){
        assert.expect(1);

        this.data.partner.records[0].foo="[]";

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:`
                <form>
                    <fieldname="foo"widget="domain"options="{'model':'partner_type'}"context="{'tree_view_ref':3}"/>
                </form>
            `,
            archs:{
                'partner_type,false,list':'<tree><fieldname="display_name"/></tree>',
                'partner_type,3,list':'<tree><fieldname="id"/></tree>',
                'partner_type,false,search':'<search><fieldname="name"string="Name"/></search>',
            },
            res_id:1,
        });

        awaittestUtils.dom.click(form.$(".o_domain_show_selection_button"));

        assert.strictEqual($('.modal.o_data_row').text(),'1214',
            "shouldhavepickedthecorrectlistview");

        form.destroy();
    });

    QUnit.module('FieldProgressBar');

    QUnit.test('FieldProgressBar:max_valueshouldupdate',asyncfunction(assert){
        assert.expect(3);

        this.data.partner.records=this.data.partner.records.slice(0,1);
        this.data.partner.records[0].qux=2;

        this.data.partner.onchanges={
            display_name:function(obj){
                obj.int_field=999;
                obj.qux=5;
            }
        };

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<form>'+
                    '<fieldname="display_name"/>'+
                    '<fieldname="qux"invisible="1"/>'+
                    '<fieldname="int_field"widget="progressbar"options="{\'current_value\':\'int_field\',\'max_value\':\'qux\'}"/>'+
                '</form>',
            res_id:1,
            viewOptions:{
                mode:'edit',
            },
            mockRPC:function(route,args){
                if(args.method==='write'){
                    assert.deepEqual(
                        args.args[1],
                        {int_field:999,qux:5,display_name:'newname'},
                        'Newvalueofprogressbarsaved');
                }
                returnthis._super.apply(this,arguments);
            }
        });

        assert.strictEqual(form.$('.o_progressbar_value').text(),'10/2',
            'Theinitialvalueoftheprogressbarshouldbecorrect');

        //triggertheonchange
        awaittestUtils.fields.editInput(form.$('.o_input[name=display_name]'),'newname');

        assert.strictEqual(form.$('.o_progressbar_value').text(),'999/5',
            'Thevalueoftheprogressbarshouldbecorrectaftertheupdate');

        awaittestUtilsDom.click(form.$buttons.find('.o_form_button_save'));

        form.destroy();
    });

    QUnit.test('FieldProgressBar:valueshouldnotupdateinreadonlymodewhenslidingthebar',asyncfunction(assert){
        assert.expect(4);
        this.data.partner.records[0].int_field=99;

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<form>'+
                    '<fieldname="int_field"widget="progressbar"options="{\'editable\':true}"/>'+
                '</form>',
            res_id:1,
            mockRPC:function(route,args){
                assert.step(route);
                returnthis._super.apply(this,arguments);
            }
        });
        var$view=$('#qunit-fixture').contents();
        $view.prependTo('body');//=>selectwithclickposition

        assert.strictEqual(form.$('.o_progressbar_value').text(),'99%',
            'Initialvalueshouldbecorrect')

        var$progressBarEl=form.$('.o_progress');
        vartop=$progressBarEl.offset().top+5;
        varleft=$progressBarEl.offset().left+5;
        try{
            testUtils.triggerPositionalMouseEvent(left,top,"click");
        }catch(e){
            form.destroy();
            $view.remove();
            thrownewError('Thetestfailstosimulateaclickinthescreen.Yourscreenisprobablytoosmalloryourdevtoolsisopen.');
        }
        assert.strictEqual(form.$('.o_progressbar_value').text(),'99%',
            'Newvalueshouldbedifferentthaninitialafterclick');

        assert.verifySteps(["/web/dataset/call_kw/partner/read"]);

        form.destroy();
        $view.remove();
    });

    QUnit.test('FieldProgressBar:valueshouldnotupdateineditmodewhenslidingthebar',asyncfunction(assert){
        assert.expect(6);
        this.data.partner.records[0].int_field=99;

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<form>'+
                    '<fieldname="int_field"widget="progressbar"options="{\'editable\':true}"/>'+
                '</form>',
            res_id:1,
            viewOptions:{
                mode:'edit',
            },
            mockRPC:function(route,args){
                assert.step(route);
                returnthis._super.apply(this,arguments);
            }
        });
        var$view=$('#qunit-fixture').contents();
        $view.prependTo('body');//=>selectwithclickposition

        assert.ok(form.$('.o_form_view').hasClass('o_form_editable'),'Formineditmode');

        assert.strictEqual(form.$('.o_progressbar_value').text(),'99%',
            'Initialvalueshouldbecorrect')

        var$progressBarEl=form.$('.o_progress');
        vartop=$progressBarEl.offset().top+5;
        varleft=$progressBarEl.offset().left+5;
        try{
            testUtils.triggerPositionalMouseEvent(left,top,"click");
        }catch(e){
            form.destroy();
            $view.remove();
            thrownewError('Thetestfailstosimulateaclickinthescreen.Yourscreenisprobablytoosmalloryourdevtoolsisopen.');
        }
        assert.strictEqual(form.$('.o_progressbar_value.o_input').val(),"99",
            'Valueofinputisnotchanged');
        awaittestUtilsDom.click(form.$buttons.find('.o_form_button_save'));

        assert.strictEqual(form.$('.o_progressbar_value').text(),'99%',
            'Newvalueshouldbedifferentthaninitialafterclick');

        assert.verifySteps(["/web/dataset/call_kw/partner/read"]);

        form.destroy();
        $view.remove();
    });

    QUnit.test('FieldProgressBar:valueshouldupdateineditmodewhentypingininput',asyncfunction(assert){
        assert.expect(5);
        this.data.partner.records[0].int_field=99;

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<form>'+
                    '<fieldname="int_field"widget="progressbar"options="{\'editable\':true}"/>'+
                '</form>',
            res_id:1,
            viewOptions:{
                mode:'edit',
            },
            mockRPC:function(route,args){
                if(args.method==='write'){
                    assert.strictEqual(args.args[1].int_field,69,
                        'Newvalueofprogressbarsaved');
                }
                returnthis._super.apply(this,arguments);
            }
        });

        assert.ok(form.$('.o_form_view').hasClass('o_form_editable'),'Formineditmode');

        assert.strictEqual(form.$('.o_progressbar_value').text(),'99%',
            'Initialvalueshouldbecorrect');

        awaittestUtilsDom.click(form.$('.o_progress'));

        var$valInput=form.$('.o_progressbar_value.o_input');
        assert.strictEqual($valInput.val(),'99','Initialvalueininputiscorrect');

        awaittestUtils.fields.editAndTrigger($valInput,'69',['input','blur']);

        awaittestUtilsDom.click(form.$buttons.find('.o_form_button_save'));

        assert.strictEqual(form.$('.o_progressbar_value').text(),'69%',
            'Newvalueshouldbedifferentthaninitialafterclick');

        form.destroy();
    });

    QUnit.test('FieldProgressBar:valueshouldupdateineditmodewhentypingininputwithfieldmaxvalue',asyncfunction(assert){
        assert.expect(5);
        this.data.partner.records[0].int_field=99;

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<form>'+
                    '<fieldname="qux"invisible="1"/>'+
                    '<fieldname="int_field"widget="progressbar"options="{\'editable\':true,\'max_value\':\'qux\'}"/>'+
                '</form>',
            res_id:1,
            viewOptions:{
                mode:'edit',
            },
            mockRPC:function(route,args){
                if(args.method==='write'){
                    assert.strictEqual(args.args[1].int_field,69,
                        'Newvalueofprogressbarsaved');
                }
                returnthis._super.apply(this,arguments);
            }
        });

        assert.ok(form.$('.o_form_view').hasClass('o_form_editable'),'Formineditmode');

        assert.strictEqual(form.$('.o_progressbar_value').text(),'99/0',
            'Initialvalueshouldbecorrect');

        awaittestUtilsDom.click(form.$('.o_progress'));

        var$valInput=form.$('.o_progressbar_value.o_input');
        assert.strictEqual($valInput.val(),'99','Initialvalueininputiscorrect');

        awaittestUtils.fields.editAndTrigger($valInput,'69',['input','blur']);

        awaittestUtilsDom.click(form.$buttons.find('.o_form_button_save'));

        assert.strictEqual(form.$('.o_progressbar_value').text(),'69/0',
            'Newvalueshouldbedifferentthaninitialafterclick');

        form.destroy();
    });

    QUnit.test('FieldProgressBar:maxvalueshouldupdateineditmodewhentypingininputwithfieldmaxvalue',asyncfunction(assert){
        assert.expect(5);
        this.data.partner.records[0].int_field=99;

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<form>'+
                    '<fieldname="qux"invisible="1"/>'+
                    '<fieldname="int_field"widget="progressbar"options="{\'editable\':true,\'max_value\':\'qux\',\'edit_max_value\':true}"/>'+
                '</form>',
            res_id:1,
            viewOptions:{
                mode:'edit',
            },
            mockRPC:function(route,args){
                if(args.method==='write'){
                    assert.strictEqual(args.args[1].qux,69,
                        'Newvalueofprogressbarsaved');
                }
                returnthis._super.apply(this,arguments);
            }
        });

        assert.ok(form.$('.o_form_view').hasClass('o_form_editable'),'Formineditmode');

        assert.strictEqual(form.$('.o_progressbar_value').text(),'99/0',
            'Initialvalueshouldbecorrect');

        awaittestUtilsDom.click(form.$('.o_progress'));

        var$valInput=form.$('.o_progressbar_value.o_input');
        assert.strictEqual($valInput.val(),"0.44444",'Initialvalueininputiscorrect');

        awaittestUtils.fields.editAndTrigger($valInput,'69',['input','blur']);

        awaittestUtilsDom.click(form.$buttons.find('.o_form_button_save'));

        assert.strictEqual(form.$('.o_progressbar_value').text(),'99/69',
            'Newvalueshouldbedifferentthaninitialafterclick');

        form.destroy();
    });

    QUnit.test('FieldProgressBar:Standardreadonlymodeisreadonly',asyncfunction(assert){
        assert.expect(5);
        this.data.partner.records[0].int_field=99;

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<form>'+
                    '<fieldname="qux"invisible="1"/>'+
                    '<fieldname="int_field"widget="progressbar"options="{\'editable\':true,\'max_value\':\'qux\',\'edit_max_value\':true}"/>'+
                '</form>',
            res_id:1,
            mockRPC:function(route,args){
                assert.step(route);
                returnthis._super.apply(this,arguments);
            }
        });

        assert.ok(form.$('.o_form_view').hasClass('o_form_readonly'),'Forminreadonlymode');

        assert.strictEqual(form.$('.o_progressbar_value').text(),'99/0',
            'Initialvalueshouldbecorrect');

        awaittestUtilsDom.click(form.$('.o_progress'));

        assert.containsNone(form,'.o_progressbar_value.o_input','noinputinreadonlymode');

        assert.verifySteps(["/web/dataset/call_kw/partner/read"]);

        form.destroy();
    });

    QUnit.test('FieldProgressBar:maxvalueshouldupdateinreadonlymodewithrightparameterwhentypingininputwithfieldmaxvalue',asyncfunction(assert){
        assert.expect(5);
        this.data.partner.records[0].int_field=99;

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<form>'+
                    '<fieldname="qux"invisible="1"/>'+
                    '<fieldname="int_field"widget="progressbar"options="{\'editable\':true,\'max_value\':\'qux\',\'edit_max_value\':true,\'editable_readonly\':true}"/>'+
                '</form>',
            res_id:1,
            mockRPC:function(route,args){
                if(args.method==='write'){
                    assert.strictEqual(args.args[1].qux,69,
                        'Newvalueofprogressbarsaved');
                }
                returnthis._super.apply(this,arguments);
            }
        });

        assert.ok(form.$('.o_form_view').hasClass('o_form_readonly'),'Forminreadonlymode');

        assert.strictEqual(form.$('.o_progressbar_value').text(),'99/0',
            'Initialvalueshouldbecorrect');

        awaittestUtilsDom.click(form.$('.o_progress'));

        var$valInput=form.$('.o_progressbar_value.o_input');
        assert.strictEqual($valInput.val(),"0.44444",'Initialvalueininputiscorrect');

        awaittestUtils.fields.editAndTrigger($valInput,'69',['input','blur']);

        assert.strictEqual(form.$('.o_progressbar_value').text(),'99/69',
            'Newvalueshouldbedifferentthaninitialafterchangingit');

        form.destroy();
    });

    QUnit.test('FieldProgressBar:valueshouldupdateinreadonlymodewithrightparameterwhentypingininputwithfieldvalue',asyncfunction(assert){
        assert.expect(5);
        this.data.partner.records[0].int_field=99;

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<form>'+
                    '<fieldname="int_field"widget="progressbar"options="{\'editable\':true,\'editable_readonly\':true}"/>'+
                '</form>',
            res_id:1,
            mockRPC:function(route,args){
                if(args.method==='write'){
                    assert.strictEqual(args.args[1].int_field,69,
                        'Newvalueofprogressbarsaved');
                }
                returnthis._super.apply(this,arguments);
            }
        });

        assert.ok(form.$('.o_form_view').hasClass('o_form_readonly'),'Forminreadonlymode');

        assert.strictEqual(form.$('.o_progressbar_value').text(),'99%',
            'Initialvalueshouldbecorrect');

        awaittestUtilsDom.click(form.$('.o_progress'));

        var$valInput=form.$('.o_progressbar_value.o_input');
        assert.strictEqual($valInput.val(),"99",'Initialvalueininputiscorrect');

        awaittestUtils.fields.editAndTrigger($valInput,'69.6',['input','blur']);

        assert.strictEqual(form.$('.o_progressbar_value').text(),'69%',
            'Newvalueshouldbedifferentthaninitialafterchangingit');

        form.destroy();
    });

    QUnit.test('FieldProgressBar:writefloatinsteadofintworks,inlocale',asyncfunction(assert){
        assert.expect(5);
        this.data.partner.records[0].int_field=99;

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<form>'+
                    '<fieldname="int_field"widget="progressbar"options="{\'editable\':true}"/>'+
                '</form>',
            res_id:1,
            viewOptions:{
                mode:'edit',
            },
            translateParameters:{
                thousands_sep:"#",
                decimal_point:":",
            },
            mockRPC:function(route,args){
                if(args.method==='write'){
                    assert.strictEqual(args.args[1].int_field,1037,
                        'Newvalueofprogressbarsaved');
                }
                returnthis._super.apply(this,arguments);
            }
        });

        assert.ok(form.$('.o_form_view').hasClass('o_form_editable'),'Formineditmode');

        assert.strictEqual(form.$('.o_progressbar_value').text(),'99%',
            'Initialvalueshouldbecorrect');

        awaittestUtilsDom.click(form.$('.o_progress'));

        var$valInput=form.$('.o_progressbar_value.o_input');
        assert.strictEqual($valInput.val(),'99','Initialvalueininputiscorrect');

        awaittestUtils.fields.editAndTrigger($valInput,'1#037:9',['input','blur']);

        awaittestUtilsDom.click(form.$buttons.find('.o_form_button_save'));

        assert.strictEqual(form.$('.o_progressbar_value').text(),'1k%',
            'Newvalueshouldbedifferentthaninitialafterclick');

        form.destroy();
    });

    QUnit.test('FieldProgressBar:writegibbrishinsteadofintthrowswarning',asyncfunction(assert){
        assert.expect(5);
        this.data.partner.records[0].int_field=99;

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<form>'+
                    '<fieldname="int_field"widget="progressbar"options="{\'editable\':true}"/>'+
                '</form>',
            res_id:1,
            viewOptions:{
                mode:'edit',
            },
            interceptsPropagate:{
                call_service:function(ev){
                    if(ev.data.service==='notification'){
                        assert.strictEqual(ev.data.method,'notify');
                        assert.strictEqual(
                            ev.data.args[0].message,
                            "Pleaseenteranumericalvalue"
                        );
                    }
                }
            },
        });

        assert.ok(form.$('.o_form_view').hasClass('o_form_editable'),'Formineditmode');

        assert.strictEqual(form.$('.o_progressbar_value').text(),'99%',
            'Initialvalueshouldbecorrect');

        awaittestUtilsDom.click(form.$('.o_progress'));

        var$valInput=form.$('.o_progressbar_value.o_input');
        assert.strictEqual($valInput.val(),'99','Initialvalueininputiscorrect');

        awaittestUtils.fields.editAndTrigger($valInput,'trenteseptvirguleneuf',['input']);

        form.destroy();
    });

    QUnit.module('FieldColor',{
        before:function(){
            returnajax.loadXML('/web/static/src/xml/colorpicker.xml',core.qweb);
        },
    });

    QUnit.test('FieldColor:defaultwidgetstate',asyncfunction(assert){
        assert.expect(4);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:
                '<form>'+
                    '<fieldname="hex_color"widget="color"/>'+
                '</form>',
            res_id:1,
            viewOptions:{
                mode:'edit',
            },
        });

        awaittestUtils.dom.click(form.$('.o_field_color'));
        assert.containsOnce($,'.modal');
        assert.containsNone($('.modal'),'.o_opacity_slider',
            "Opacityslidershouldnotbepresent");
        assert.containsNone($('.modal'),'.o_opacity_input',
            "Opacityinputshouldnotbepresent");

        awaittestUtils.dom.click($('.modal.btn:contains("Discard")'));

        assert.strictEqual(document.activeElement,form.$('.o_field_color')[0],
            "Focusshouldgobacktothecolorfield");

        form.destroy();
    });

    QUnit.test('FieldColor:behaviourindifferentviews',asyncfunction(assert){
        assert.expect(2);

        this.data.partner.records[0].p=[4,2];
        this.data.partner.records[1].hex_color='#ff0080';

        constform=awaitcreateView({
            arch:'<form>'+
                    '<fieldname="hex_color"widget="color"/>'+
                    '<fieldname="p">'+
                        '<treeeditable="top">'+
                            '<fieldname="display_name"/>'+
                            '<fieldname="hex_color"widget="color"/>'+
                        '</tree>'+
                    '</field>'+
                '</form>',
            data:this.data,
            model:'partner',
            res_id:1,
            View:FormView,
        });

        awaittestUtils.dom.click(form.$('.o_field_color:first()'));
        assert.containsNone($(document.body),'.modal',
            "Colorfieldinreadonlyshouldn'tbeeditable");

        constrowInitialHeight=form.$('.o_data_row:first()').height();

        awaittestUtils.form.clickEdit(form);
        awaittestUtils.dom.click(form.$('.o_data_row:first().o_data_cell:first()'));

        assert.strictEqual(rowInitialHeight,form.$('.o_data_row:first()').height(),
            "Colorfieldshouldn'tchangethecolorheightwhenedited");

        form.destroy();
    });

    QUnit.test('FieldColor:pickandresetcolors',asyncfunction(assert){
        assert.expect(2);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:
                '<form>'+
                    '<fieldname="hex_color"widget="color"/>'+
                '</form>',
            res_id:1,
            viewOptions:{
                mode:'edit',
            },
        });

        assert.strictEqual($('.o_field_color').css('backgroundColor'),'rgb(255,0,0)',
            "Backgroundofthecolorfieldshouldbeinitiallyred");

        awaittestUtils.dom.click(form.$('.o_field_color'));
        awaittestUtils.fields.editAndTrigger($('.modal.o_hex_input'),'#00ff00',['change']);
        awaittestUtils.dom.click($('.modal.btn:contains("Choose")'));

        assert.strictEqual($('.o_field_color').css('backgroundColor'),'rgb(0,255,0)',
            "Backgroundofthecolorfieldshouldbeupdatedtogreen");

        form.destroy();
    });

    QUnit.module('FieldColorPicker');

    QUnit.test('FieldColorPicker:cannavigateawaywithTAB',asyncfunction(assert){
        assert.expect(1);

        constform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:`
                <formstring="Partners">
                    <fieldname="int_field"widget="color_picker"/>
                    <fieldname="foo"/>
                </form>`,
            res_id:1,
            viewOptions:{
                mode:'edit',
            },
        });

        form.$el.find('a.oe_kanban_color_1')[0].focus();

        form.$el.find('a.oe_kanban_color_1').trigger($.Event('keydown',{
            which:$.ui.keyCode.TAB,
            keyCode:$.ui.keyCode.TAB,
        }));
        assert.strictEqual(document.activeElement,form.$el.find('input[name="foo"]')[0],
            "foofieldshouldbefocused");
        form.destroy();
    });


    QUnit.module('FieldBadge');

    QUnit.test('FieldBadgecomponentonacharfieldinlistview',asyncfunction(assert){
        assert.expect(3);

        constlist=awaitcreateView({
            View:ListView,
            model:'partner',
            data:this.data,
            arch:`<list><fieldname="display_name"widget="badge"/></list>`,
        });

        assert.containsOnce(list,'.o_field_badge[name="display_name"]:contains(firstrecord)');
        assert.containsOnce(list,'.o_field_badge[name="display_name"]:contains(secondrecord)');
        assert.containsOnce(list,'.o_field_badge[name="display_name"]:contains(aaa)');

        list.destroy();
    });

    QUnit.test('FieldBadgecomponentonaselectionfieldinlistview',asyncfunction(assert){
        assert.expect(3);

        constlist=awaitcreateView({
            View:ListView,
            model:'partner',
            data:this.data,
            arch:`<list><fieldname="selection"widget="badge"/></list>`,
        });

        assert.containsOnce(list,'.o_field_badge[name="selection"]:contains(Blocked)');
        assert.containsOnce(list,'.o_field_badge[name="selection"]:contains(Normal)');
        assert.containsOnce(list,'.o_field_badge[name="selection"]:contains(Done)');

        list.destroy();
    });

    QUnit.test('FieldBadgecomponentonamany2onefieldinlistview',asyncfunction(assert){
        assert.expect(2);

        constlist=awaitcreateView({
            View:ListView,
            model:'partner',
            data:this.data,
            arch:`<list><fieldname="trululu"widget="badge"/></list>`,
        });

        assert.containsOnce(list,'.o_field_badge[name="trululu"]:contains(firstrecord)');
        assert.containsOnce(list,'.o_field_badge[name="trululu"]:contains(aaa)');

        list.destroy();
    });

    QUnit.test('FieldBadgecomponentwithdecoration-xxxattributes',asyncfunction(assert){
        assert.expect(6);

        constlist=awaitcreateView({
            View:ListView,
            model:'partner',
            data:this.data,
            arch:`
                <list>
                    <fieldname="selection"/>
                    <fieldname="foo"widget="badge"decoration-danger="selection=='done'"decoration-warning="selection=='blocked'"/>
                </list>`,
        });

        assert.containsN(list,'.o_field_badge[name="foo"]',5);
        assert.containsOnce(list,'.o_field_badge[name="foo"].bg-danger-light');
        assert.containsOnce(list,'.o_field_badge[name="foo"].bg-warning-light');

        awaitlist.reload();

        assert.containsN(list,'.o_field_badge[name="foo"]',5);
        assert.containsOnce(list,'.o_field_badge[name="foo"].bg-danger-light');
        assert.containsOnce(list,'.o_field_badge[name="foo"].bg-warning-light');

        list.destroy();
    });
});
});
});
