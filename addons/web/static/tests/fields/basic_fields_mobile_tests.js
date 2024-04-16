flectra.define('web.basic_fields_mobile_tests',function(require){
"usestrict";

varFormView=require('web.FormView');
varListView=require('web.ListView');
vartestUtils=require('web.test_utils');

varcreateView=testUtils.createView;

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
                    int_field:{string:"int_field",type:"integer",sortable:true,searchable:true},
                    qux:{string:"Qux",type:"float",digits:[16,1],searchable:true},
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
                },{
                    id:2,
                    display_name:"secondrecord",
                    bar:true,
                    foo:"blip",
                    int_field:0,
                    qux:0,
                },{
                    id:4,
                    display_name:"aaa",
                    foo:"abc",
                    int_field:false,
                    qux:false,
                }],
                onchanges:{},
            },
        };
    }
},function(){

    QUnit.module('PhoneWidget');

    QUnit.test('phonefieldinformviewonextrasmallscreens',asyncfunction(assert){
        assert.expect(7);

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
        });

        var$phoneLink=form.$('a.o_form_uri.o_field_widget');
        assert.strictEqual($phoneLink.length,1,
            "shouldhaveaanchorwithcorrectclasses");
        assert.strictEqual($phoneLink.text(),'yop',
            "valueshouldbedisplayedproperly");
        assert.hasAttrValue($phoneLink,'href','tel:yop',
            "shouldhavepropertelprefix");

        //switchtoeditmodeandchecktheresult
        awaittestUtils.form.clickEdit(form);
        assert.containsOnce(form,'input[type="text"].o_field_widget',
            "shouldhaveanintforthephonefield");
        assert.strictEqual(form.$('input[type="text"].o_field_widget').val(),'yop',
            "inputshouldcontainfieldvalueineditmode");

        //changevalueineditmode
        awaittestUtils.fields.editInput(form.$('input[type="text"].o_field_widget'),'new');

        //save
        awaittestUtils.form.clickSave(form);
        $phoneLink=form.$('a.o_form_uri.o_field_widget');
        assert.strictEqual($phoneLink.text(),'new',
            "newvalueshouldbedisplayedproperly");
        assert.hasAttrValue($phoneLink,'href','tel:new',
            "shouldstillhavepropertelprefix");

        form.destroy();
    });

    QUnit.test('phonefieldineditablelistviewonextrasmallscreens',asyncfunction(assert){
        assert.expect(10);

        varlist=awaitcreateView({
            View:ListView,
            model:'partner',
            data:this.data,
            arch:'<treeeditable="bottom"><fieldname="foo"widget="phone"/></tree>',
        });

        assert.containsN(list,'.o_data_row',3,
            "shouldhave3record");
        assert.strictEqual(list.$('tbodytd:not(.o_list_record_selector)a').first().text(),'yop',
            "valueshouldbedisplayedproperly");

        var$phoneLink=list.$('a.o_form_uri.o_field_widget');
        assert.strictEqual($phoneLink.length,3,
            "shouldhaveanchorswithcorrectclasses");
        assert.hasAttrValue($phoneLink.first(),'href','tel:yop',
            "shouldhavepropertelprefix");

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
        $phoneLink=list.$('a.o_form_uri.o_field_widget');
        assert.strictEqual($phoneLink.length,3,
            "shouldstillhaveanchorswithcorrectclasses");
        assert.hasAttrValue($phoneLink.first(),'href','tel:new',
            "shouldstillhavepropertelprefix");

        list.destroy();
    });

    QUnit.test('phonefielddoesnotallowhtmlinjections',asyncfunction(assert){
        assert.expect(1);

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
            viewOptions:{
                mode:'edit',
            },
        });

        varval='<script>throwError();</script><script>throwError();</script>';
        awaittestUtils.fields.editInput(form.$('input.o_field_widget[name="foo"]'),val);

        //save
        awaittestUtils.form.clickSave(form);
        assert.strictEqual(form.$('.o_field_widget').text(),val,
            "valueshouldhavebeencorrectlyescaped");

        form.destroy();
    });

    QUnit.module('FieldDateRange');

    QUnit.test('datefield:toggledaterangepickerthenscroll',asyncfunction(assert){
        assert.expect(4);
        constscrollEvent=newUIEvent('scroll');

        functionscrollAtHeight(height){
            window.scrollTo(0,height);
            document.dispatchEvent(scrollEvent);
        }
        this.data.partner.fields.date_end={string:'DateEnd',type:'date'};

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<form>'+
                    '<fieldname="date"widget="daterange"options="{\'related_end_date\':\'date_end\'}"/>'+
                    '<fieldname="date_end"widget="daterange"options="{\'related_start_date\':\'date\'}"/>'+
                '</form>',
            session:{
                getTZOffset:function(){
                    return330;
                },
            },
        });

        //Checkdaterangepickerinitialization
        assert.containsN(document.body,'.daterangepicker',2,
            "shouldinitialize2daterangepicker");

        //Opendaterangepicker
        awaittestUtils.dom.click("input[name=date]");
        assert.isVisible($('.daterangepicker:first'),
            "daterangepickershouldbeopened");

        //Scroll
        scrollAtHeight(50);
        assert.isVisible($('.daterangepicker:first'),
            "daterangepickershouldbeopened");

        //Closepicker
        awaittestUtils.dom.click($('.daterangepicker:first.cancelBtn'));
        assert.isNotVisible($('.daterangepicker:first'),
            "daterangepickershouldbeclosed");

        form.destroy();
    });
});
});
});
