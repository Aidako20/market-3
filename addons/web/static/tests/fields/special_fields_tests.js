flectra.define('web.special_fields_tests',function(require){
"usestrict";

varFormView=require('web.FormView');
varListView=require('web.ListView');
vartestUtils=require('web.test_utils');

varcreateView=testUtils.createView;

QUnit.module('fields',{},function(){

QUnit.module('special_fields',{
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
                    turtles:{string:"one2manyturtlefield",type:"one2many",relation:'turtle'},
                    trululu:{string:"Trululu",type:"many2one",relation:'partner'},
                    timmy:{string:"pokemon",type:"many2many",relation:'partner_type'},
                    product_id:{string:"Product",type:"many2one",relation:'product'},
                    color:{
                        type:"selection",
                        selection:[['red',"Red"],['black',"Black"]],
                        default:'red',
                    },
                    date:{string:"SomeDate",type:"date"},
                    datetime:{string:"DatetimeField",type:'datetime'},
                    user_id:{string:"User",type:'many2one',relation:'user'},
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
                    turtle_foo:{string:"Foo",type:"char",default:"MylittleFooValue"},
                    turtle_bar:{string:"Bar",type:"boolean",default:true},
                    turtle_int:{string:"int",type:"integer",sortable:true},
                    turtle_qux:{string:"Qux",type:"float",digits:[16,1],required:true,default:1.5},
                    turtle_description:{string:"Description",type:"text"},
                    turtle_trululu:{string:"Trululu",type:"many2one",relation:'partner'},
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
                    turtle_bar:false,
                    turtle_foo:"kawa",
                    turtle_int:21,
                    turtle_qux:9.8,
                    partner_ids:[],
                }],
            },
            user:{
                fields:{
                    name:{string:"Name",type:"char"}
                },
                records:[{
                    id:17,
                    name:"Aline",
                },{
                    id:19,
                    name:"Christine",
                }]
            },
        };
    }
},function(){

    QUnit.module('FieldTimezoneMismatch');

    QUnit.test('widgettimezone_mismatchinalistview',asyncfunction(assert){
        assert.expect(5);

        this.data.partner.fields.tz_offset={
            string:"tz_offset",
            type:"char"
        };
        this.data.partner.records.forEach(function(r){
            r.color='red';
            r.tz_offset=0;
        });
        this.data.partner.onchanges={
            color:function(r){
                r.tz_offset='+4800';//makesurwehaveamismatch
            }
        };

        varlist=awaitcreateView({
            View:ListView,
            model:'partner',
            data:this.data,
            arch:'<treestring="Colors"editable="top">'+
                        '<fieldname="tz_offset"invisible="True"/>'+
                        '<fieldname="color"widget="timezone_mismatch"/>'+
                '</tree>',
        });

        assert.strictEqual(list.$('td:contains(Red)').length,3,
            "shouldhave3rowswithcorrectvalue");
        awaittestUtils.dom.click(list.$('td:contains(Red):first'));

        var$td=list.$('tbodytr.o_selected_rowtd:not(.o_list_record_selector)');

        assert.strictEqual($td.find('select').length,1,"tdshouldhaveachild'select'");
        assert.strictEqual($td.contents().length,1,"selecttagshouldbeonlychildoftd");

        awaittestUtils.fields.editSelect($td.find('select'),'"black"');

        assert.strictEqual($td.find('.o_tz_warning').length,1,"Shoulddisplayiconalert");
        assert.ok($td.find('selectoption:selected').text().match(/Black\s+\([0-9]+\/[0-9]+\/[0-9]+[0-9]+:[0-9]+:[0-9]+\)/),"Shoulddisplaythedatetimeintheselectedtimezone");
        list.destroy();
    });

    QUnit.test('widgettimezone_mismatchinaformview',asyncfunction(assert){
        assert.expect(2);

        this.data.partner.fields.tz_offset={
            string:"tz_offset",
            type:"char"
        };
        this.data.partner.fields.tz={
            type:"selection",
            selection:[['Europe/Brussels',"Europe/Brussels"],['America/Los_Angeles',"America/Los_Angeles"]],
        };
        this.data.partner.records[0].tz=false;
        this.data.partner.records[0].tz_offset='+4800';

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            res_id:1,
            data:this.data,
            arch:'<form>'+
                    '<fieldname="tz_offset"invisible="True"/>'+
                    '<fieldname="tz"widget="timezone_mismatch"/>'+
                '</form>',
        });
        awaittestUtils.form.clickEdit(form);
        assert.containsOnce(form,'select[name=tz]');

        var$timezoneMismatch=form.$('.o_tz_warning');
        assert.strictEqual($timezoneMismatch.length,1,"warningclassshouldbethere.");

        form.destroy();
    });

    QUnit.test('widgettimezone_mismatchinaformvieweditmodewithmismatch',asyncfunction(assert){
        assert.expect(3);

        this.data.partner.fields.tz_offset={
            string:"tz_offset",
            type:"char"
        };
        this.data.partner.fields.tz={
            type:"selection",
            selection:[['Europe/Brussels',"Europe/Brussels"],['America/Los_Angeles',"America/Los_Angeles"]],
        };
        this.data.partner.records[0].tz='America/Los_Angeles';
        this.data.partner.records[0].tz_offset='+4800';

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            res_id:1,
            data:this.data,
            arch:'<form>'+
                    '<fieldname="tz_offset"invisible="True"/>'+
                    '<fieldname="tz"widget="timezone_mismatch"options="{\'tz_offset_field\':\'tz_offset\'}"/>'+
                '</form>',
            viewOptions:{
                mode:'edit',
            },
        });

        var$timezoneEl=form.$('select[name="tz"]');
        assert.strictEqual($timezoneEl.children().length,3,
            'Theselectelementshouldhave3children');

        var$timezoneMismatch=form.$('.o_tz_warning');
        assert.strictEqual($timezoneMismatch.length,1,
            'timezonemismatchispresent');

        assert.notOk($timezoneMismatch.children().length,
            'Themismatchelementshouldnothavechildren');
        form.destroy();
    });

    QUnit.module('FieldReportLayout');

    QUnit.test('report_layoutwidgetinformview',asyncfunction(assert){
        assert.expect(3);

        this.data['report.layout']={
            fields:{
                view_id:{string:"DocumentTemplate",type:"many2one",relation:"product"},
                image:{string:"Previewimagesrc",type:"char"},
                pdf:{string:"Previewpdfsrc",type:"char"}
            },
            records:[{
                id:1,
                view_id:37,
                image:"/web/static/toto.png",
                pdf:"/web/static/toto.pdf",
            },{
                id:2,
                view_id:41,
                image:"/web/static/tata.png",
                pdf:"/web/static/tata.pdf",
            }],
        };
        this.data.partner.records[1].product_id=false;

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<form>'+
                    '<fieldname="product_id"widget="report_layout"/>'+
                  '</form>',
            res_id:2,
            viewOptions:{
                mode:'edit',
            },
        });

        assert.strictEqual(form.$('.img.img-fluid').length,2,
            "Twoimagesshouldberendered");
        assert.strictEqual(form.$('.img.btn-info').length,0,
            "Noimageshouldbeselected");

        //selectfirstimage
        awaittestUtils.dom.click(form.$(".img.img-fluid:first"));
        assert.ok(form.$(".img.img-fluid:first").hasClass('btn-info'),
            "Firstimageshouldbeselected");

        form.destroy();
    });

    QUnit.module('IframeWrapper');

    QUnit.test('iframe_wrapperwidgetinformview',asyncfunction(assert){

        assert.expect(2);

        this.data={
            report:{
                fields:{
                    report_content:{string:"Contentofreport",type:"html"}
                },
                records:[{
                    id:1,
                    report_content:
                        `<html>
                            <head>
                                <style>
                                    body{color:rgb(255,0,0);}
                                </style>
                            <head>
                            <body>
                                <divclass="nice_div"><p>Somecontent</p></div>
                            </body>
                         </html>`
                }]
            }
        };

        constform=awaitcreateView({
            View:FormView,
            model:'report',
            data:this.data,
            arch:`<form><fieldname="report_content"widget="iframe_wrapper"/></form>`,
            res_id:1,
        });

        const$iframe=form.$('iframe');
        await$iframe.data('ready');
        constdoc=$iframe.contents()[0];

        assert.strictEqual($(doc).find('.nice_div').html(),'<p>Somecontent</p>',
            "shouldhaverenderedadivwithcorrectcontent");

        assert.strictEqual($(doc).find('.nice_divp').css('color'),'rgb(255,0,0)',
            "headtagstyleshouldhavebeenapplied");

        form.destroy();

    });


});
});
});
