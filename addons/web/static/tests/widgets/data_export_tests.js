flectra.define('web.data_export_tests',function(require){
"usestrict";

constdata=require('web.data');
constframework=require('web.framework');
constListView=require('web.ListView');
consttestUtils=require('web.test_utils');

constcpHelpers=testUtils.controlPanel;
constcreateView=testUtils.createView;

QUnit.module('widgets',{
    beforeEach:function(){
        this.data={
            'partner':{
                fields:{
                    foo:{string:"Foo",type:"char"},
                    bar:{string:"Bar",type:"char"},
                    unexportable:{string:"Unexportable",type:"boolean",exportable:false},
                },
                records:[
                    {
                        id:1,
                        foo:"yop",
                        bar:"bar-blup",
                    },{
                        id:2,
                        foo:"yop",
                        bar:"bar-yop",
                    },{
                        id:3,
                        foo:"blup",
                        bar:"bar-blup",
                    }
                ]
            },
            'ir.exports':{
                fields:{
                    name:{string:"Name",type:"char"},
                },
                records:[],
            },
        };
        this.mockSession={
            asyncuser_has_group(g){returng==='base.group_allow_export';}
        }
        this.mockDataExportRPCs=function(route){
            if(route==='/web/export/formats'){
                returnPromise.resolve([
                    {tag:'csv',label:'CSV'},
                    {tag:'xls',label:'Excel'},
                ]);
            }
            if(route==='/web/export/get_fields'){
                returnPromise.resolve([
                    {
                        field_type:"one2many",
                        string:"Activities",
                        required:false,
                        value:"activity_ids/id",
                        id:"activity_ids",
                        params:{"model":"mail.activity","prefix":"activity_ids","name":"Activities"},
                        relation_field:"res_id",
                        children:true,
                    },{
                        children:false,
                        field_type:'char',
                        id:"foo",
                        relation_field:null,
                        required:false,
                        string:'Foo',
                        value:"foo",
                    }
                ]);
            }
            returnthis._super.apply(this,arguments);
        };
    }
},function(){

    QUnit.module('DataExport');


    QUnit.test('exportingalldatainlistview',asyncfunction(assert){
        assert.expect(8);

        varblockUI=framework.blockUI;
        varunblockUI=framework.unblockUI;
        framework.blockUI=function(){
            assert.step('blockUI');
        };
        framework.unblockUI=function(){
            assert.step('unblockUI');
        };

        varlist=awaitcreateView({
            View:ListView,
            model:'partner',
            data:this.data,
            arch:'<tree><fieldname="foo"/></tree>',
            viewOptions:{
                hasActionMenus:true,
            },
            mockRPC:this.mockDataExportRPCs,
            session:{
                ...this.mockSession,
                get_file:function(params){
                    assert.step(params.url);
                    params.complete();
                },
            },
        });


        awaittestUtils.dom.click(list.$('theadth.o_list_record_selectorinput'));

        awaitcpHelpers.toggleActionMenu(list);
        awaitcpHelpers.toggleMenuItem(list,'Export');

        assert.strictEqual($('.modal').length,1,"amodaldialogshouldbeopen");
        assert.strictEqual($('div.o_tree_column:contains(Activities)').length,1,
            "theActivitiesfieldshouldbeinthelistofexportablefields");
        assert.strictEqual($('.modal.o_export_field').length,1,"Thereshouldbeonlyoneexportfield");
        assert.strictEqual($('.modal.o_export_field').data('field_id'),'foo',"Thereshouldbeonlyoneexportfield");

        //selectthefieldDescription,clickonadd,thenexportandclose
        awaittestUtils.dom.click($('.modal.o_tree_column:contains(Foo).o_add_field'));
        awaittestUtils.dom.click($('.modalspan:contains(Export)'));
        awaittestUtils.dom.click($('.modalspan:contains(Close)'));
        list.destroy();
        framework.blockUI=blockUI;
        framework.unblockUI=unblockUI;
        assert.verifySteps([
            'blockUI',
            '/web/export/csv',
            'unblockUI',
        ]);
    });

    QUnit.test('exportingdatainlistview(multipages)',asyncfunction(assert){
        assert.expect(4);

        letexpectedData;
        constlist=awaitcreateView({
            View:ListView,
            model:'partner',
            data:this.data,
            arch:'<treelimit="2"><fieldname="foo"/></tree>',
            domain:[['id','<',1000]],
            viewOptions:{
                hasActionMenus:true,
            },
            mockRPC:this.mockDataExportRPCs,
            session:{
                ...this.mockSession,
                get_file:function(params){
                    constdata=JSON.parse(params.data.data);
                    assert.deepEqual({ids:data.ids,domain:data.domain},expectedData);
                    params.complete();
                },
            },
        });

        //selectallrecords(firstpage)andexport
        expectedData={
            ids:[1,2],
            domain:[['id','<',1000]],
        };
        awaittestUtils.dom.click(list.$('theadth.o_list_record_selectorinput'));

        awaitcpHelpers.toggleActionMenu(list);
        awaitcpHelpers.toggleMenuItem(list,'Export');

        assert.containsOnce(document.body,'.modal');

        awaittestUtils.dom.click($('.modalspan:contains(Export)'));
        awaittestUtils.dom.click($('.modalspan:contains(Close)'));

        //selectalldomainandexport
        expectedData={
            ids:false,
            domain:[['id','<',1000]],
        };
        awaittestUtils.dom.click(list.$('.o_list_selection_box.o_list_select_domain'));

        awaitcpHelpers.toggleActionMenu(list);
        awaitcpHelpers.toggleMenuItem(list,'Export');

        assert.containsOnce(document.body,'.modal');

        awaittestUtils.dom.click($('.modalspan:contains(Export)'));
        awaittestUtils.dom.click($('.modalspan:contains(Close)'));

        list.destroy();
    });

    QUnit.test('exportingviewwithnon-exportablefield',asyncfunction(assert){
        assert.expect(0);

        varlist=awaitcreateView({
            View:ListView,
            model:'partner',
            data:this.data,
            arch:'<tree><fieldname="unexportable"/></tree>',
            viewOptions:{
                hasActionMenus:true,
            },
            mockRPC:this.mockDataExportRPCs,
            session:{
                ...this.mockSession,
                get_file:function(params){
                    assert.step(params.url);
                    params.complete();
                },
            },
        });

        awaittestUtils.dom.click(list.$('theadth.o_list_record_selectorinput'));

        awaitcpHelpers.toggleActionMenu(list);
        awaitcpHelpers.toggleMenuItem(list,'Export');

        list.destroy();
    });

    QUnit.test('savingfieldslistwhenexportingdata',asyncfunction(assert){
        assert.expect(4);

        varcreate=data.DataSet.prototype.create;

        data.DataSet.prototype.create=function(){
            assert.step('create');
            returnPromise.resolve([]);
        };

        varlist=awaitcreateView({
            View:ListView,
            model:'partner',
            data:this.data,
            arch:'<tree><fieldname="foo"/></tree>',
            viewOptions:{
                hasActionMenus:true,
            },
            session:this.mockSession,
            mockRPC:this.mockDataExportRPCs,
        });


        //Opentheexportmodal
        awaittestUtils.dom.click(list.$('theadth.o_list_record_selectorinput'));
        awaitcpHelpers.toggleActionMenu(list);
        awaitcpHelpers.toggleMenuItem(list,'Export');

        assert.strictEqual($('.modal').length,1,
            "amodaldialogshouldbeopen");

        //Select'Activities'infieldstoexport
        awaittestUtils.dom.click($('.modal.o_export_tree_item:contains(Activities).o_add_field'));
        assert.strictEqual($('.modal.o_fields_list.o_export_field').length,2,
            "thereshouldbetwoitemsinthefieldslist");
        //Saveastemplate
        awaittestUtils.fields.editAndTrigger($('.modal.o_exported_lists_select'),'new_template',['change']);
        awaittestUtils.fields.editInput($('.modal.o_save_list.o_save_list_name'),'fieldslist');
        awaittestUtils.dom.click($('.modal.o_save_list.o_save_list_btn'));

        assert.verifySteps(['create'],
            "createshouldhavebeencalled");

        //Closethemodalanddestroylist
        awaittestUtils.dom.click($('.modalbuttonspan:contains(Close)'));
        list.destroy();

        //restorecreatefunction
        data.DataSet.prototype.create=create;
    });

    QUnit.test('ExportdialogUItest',asyncfunction(assert){
        assert.expect(5);
        varlist=awaitcreateView({
            View:ListView,
            model:'partner',
            data:this.data,
            arch:'<tree><fieldname="foo"/></tree>',
            viewOptions:{
                hasActionMenus:true,
            },
            session:this.mockSession,
            mockRPC:this.mockDataExportRPCs,
        });


        //Opentheexportmodal
        awaittestUtils.dom.click(list.$('theadth.o_list_record_selectorinput'));
        awaitcpHelpers.toggleActionMenu(list);
        awaitcpHelpers.toggleMenuItem(list,'Export');

        assert.strictEqual($('.modal.o_export_tree_item:visible').length,2,"Thereshouldbeonlytwoitemsvisible");
        awaittestUtils.dom.click($('.modal.o_export_search_input'));
        $('.modal.o_export_search_input').val('Activities').trigger($.Event('input',{
            keyCode:65,
        }));
        assert.strictEqual($('.modal.o_export_tree_item:visible').length,1,"Onlymatchitemvisible");
        //Addfield
        awaittestUtils.dom.click($('.modaldiv:contains(Activities).o_add_field'));
        assert.strictEqual($('.modal.o_fields_listli').length,2,"Thereshouldbetwofieldsinexportfieldlist.");
        assert.strictEqual($('.modal.o_fields_listli:eq(1)').text(),"Activities",
            "stringofsecondfieldinexportlistshouldbe'Activities'");
        //Removefield
        awaittestUtils.dom.click($('.modal.o_fields_listli:first.o_remove_field'));
        assert.strictEqual($('.modal.o_fields_listli').length,1,"Thereshouldbeonlyonefieldinlist");
        list.destroy();
    });

    QUnit.test('Directexportbuttoninvisible',asyncfunction(assert){
        assert.expect(1)

        letlist=awaitcreateView({
            View:ListView,
            model:'partner',
            data:this.data,
            arch:`<treeexport_xlsx="0"><fieldname="foo"/></tree>`,
            session:this.mockSession,
        });
        assert.containsNone(list,'.o_list_export_xlsx')
        list.destroy();
    });

    QUnit.test('Directexportlist',asyncfunction(assert){
        assert.expect(2);

        letlist=awaitcreateView({
            View:ListView,
            model:'partner',
            data:this.data,
            arch:`
                <treeexport_xlsx="1">
                    <fieldname="foo"/>
                    <fieldname="bar"/>
                </tree>`,
            domain:[['bar','!=','glou']],
            session:{
                ...this.mockSession,
                get_file(args){
                    letdata=JSON.parse(args.data.data);
                    assert.strictEqual(args.url,'/web/export/xlsx',"shouldcallget_filewiththecorrecturl");
                    assert.deepEqual(data,{
                        context:{},
                        model:'partner',
                        domain:[['bar','!=','glou']],
                        groupby:[],
                        ids:false,
                        import_compat:false,
                        fields:[{
                            name:'foo',
                            label:'Foo',
                            type:'char',
                        },{
                            name:'bar',
                            label:'Bar',
                            type:'char',
                        }]
                    },"shouldbecalledwithcorrectparams");
                    args.complete();
                },
            },
        });

        //Download
        awaittestUtils.dom.click(list.$buttons.find('.o_list_export_xlsx'));

        list.destroy();
    });

    QUnit.test('Directexportgroupedlist',asyncfunction(assert){
        assert.expect(2);

        letlist=awaitcreateView({
            View:ListView,
            model:'partner',
            data:this.data,
            arch:`
                <tree>
                    <fieldname="foo"/>
                    <fieldname="bar"/>
                </tree>`,
            groupBy:['foo','bar'],
            domain:[['bar','!=','glou']],
            session:{
                ...this.mockSession,
                get_file(args){
                    letdata=JSON.parse(args.data.data);
                    assert.strictEqual(args.url,'/web/export/xlsx',"shouldcallget_filewiththecorrecturl");
                    assert.deepEqual(data,{
                        context:{},
                        model:'partner',
                        domain:[['bar','!=','glou']],
                        groupby:['foo','bar'],
                        ids:false,
                        import_compat:false,
                        fields:[{
                            name:'foo',
                            label:'Foo',
                            type:'char',
                        },{
                            name:'bar',
                            label:'Bar',
                            type:'char',
                        }]
                    },"shouldbecalledwithcorrectparams");
                    args.complete();
                },
            },
        });

        awaittestUtils.dom.click(list.$buttons.find('.o_list_export_xlsx'));

        list.destroy();
    });
});

});
