flectra.define('web.singleton_list_tests',function(require){
"usestrict";

varSingletonListView=require('stock.SingletonListView');
vartestUtils=require('web.test_utils');

varcreateView=testUtils.createView;


QUnit.module('Views',{
    beforeEach:function(){
        this.data={
            person:{
                fields:{
                    name:{string:"Name",type:"char"},
                    age:{string:"Age",type:"integer"},
                    job:{string:"Profession",type:"char"},
                },
                records:[
                    {id:1,name:'DanielFortesque',age:32,job:'Soldier'},
                    {id:2,name:'SamuelOak',age:64,job:'Professor'},
                    {id:3,name:'LetoIIAtreides',age:128,job:'Emperor'},
                ]
            },
        };
        this.mockRPC=function(route,args){
            if(route==='/web/dataset/call_kw/person/create'){
                varname=args.args[0].name;
                varage=args.args[0].age;
                varjob=args.args[0].job;
                for(vardofthis.data.person.records){
                    if(d.name===name){
                        d.age=age;
                        d.job=job;
                        returnPromise.resolve(d.id);
                    }
                }
            }
            returnthis._super.apply(this,arguments);
        };
    }
},function(){

    QUnit.module('SingletonListView');

    QUnit.test('Createnewrecordcorrectly',asyncfunction(assert){
        assert.expect(2);

        varlist=awaitcreateView({
            View:SingletonListView,
            model:'person',
            data:this.data,
            arch:'<treeeditable="top"js_class="singleton_list">'+
                    '<fieldname="name"/>'+
                    '<fieldname="age"/>'+
                   '</tree>',
            mockRPC:this.mockRPC,
        });
        //Checkswehaveinitially3records
        assert.containsN(list,'.o_data_row',3,"shouldhave3records");

        //Createsanewline...
        awaittestUtils.dom.click($('.o_list_button_add'));
        //...andfillsfieldswithnewvalues
        var$input=$('.o_selected_rowinput[name=name]');
        awaittestUtils.fields.editInput($input,'Bilou');
        awaittestUtils.fields.triggerKeydown($input,'tab');

        $input=$('.o_selected_rowinput[name=age]');
        awaittestUtils.fields.editInput($input,'24');
        awaittestUtils.fields.triggerKeydown($input,'enter');
        awaittestUtils.dom.click($('.o_list_button_save'));

        //Checksnewrecordisinthelist
        assert.containsN(list,'.o_data_row',4,"shouldnowhave4records");
        list.destroy();
    });

    QUnit.test('Don\'tduplicaterecord',asyncfunction(assert){
        assert.expect(3);

        varlist=awaitcreateView({
            View:SingletonListView,
            model:'person',
            data:this.data,
            arch:'<treeeditable="top"js_class="singleton_list">'+
                    '<fieldname="name"/>'+
                    '<fieldname="age"/>'+
                   '</tree>',
            mockRPC:this.mockRPC,
        });
        //Checkswehaveinitially3records
        assert.containsN(list,'.o_data_row',3,"shouldhave3records");

        //Createsanewline...
        awaittestUtils.dom.click($('.o_list_button_add'));
        //...andfillsfieldswithalreadyexistingvalue
        var$input=$('.o_selected_rowinput[name=name]');
        varname='SamuelOak';
        awaittestUtils.fields.editInput($input,name);
        awaittestUtils.fields.triggerKeydown($input,'tab');

        $input=$('.o_selected_rowinput[name=age]');
        varage='72';
        awaittestUtils.fields.editInput($input,age);
        awaittestUtils.fields.triggerKeydown($input,'enter');

        //Checkswehavestillonly3records...
        assert.containsN(list,'.o_data_row',3,"shouldstillhave3records");
        //...andverifymodificationwasoccured.
        varnameField=list.$('td[title="'+name+'"]');
        varageField=nameField.parent().find('.o_list_number');
        assert.strictEqual(ageField.text(),age,"Theagefieldmustbeupdated");
        list.destroy();
    });

    QUnit.test('Don\'traiseerrorwhentryingtocreateduplicateline',asyncfunction(assert){
        assert.expect(3);
       /*Insomecondition,alisteditablewiththe`singletonlist`js_class
       cantrytoselectarecordatalinewhoisn'tthesameplaceanymore.
       Inthiscase,thelistcantrytofindtheidofanundefinedrecord.
       Thistestjustinsureswedon'traiseatracebackinthiscase.
       */
        varlist=awaitcreateView({
            View:SingletonListView,
            model:'person',
            data:{
                person:{
                    fields:{
                        name:{string:"Name",type:"char"},
                        age:{string:"Age",type:"integer"},
                    },
                    records:[
                        {id:1,name:'BobbyB.Bop',age:18},
                    ]
                }
            },
            arch:'<treeeditable="top"js_class="singleton_list">'+
                    '<fieldname="name"/>'+
                    '<fieldname="age"/>'+
                   '</tree>',
            mockRPC:this.mockRPC,
        });
        //Checkswehaveinitially1record
        assert.containsN(list,'.o_data_row',1,"shouldhave1records");

        //Createsanewline...
        awaittestUtils.dom.click($('.o_list_button_add'));
        //...andfillsfieldswithalreadyexistingvalue
        var$input=$('.o_selected_rowinput[name=name]');
        varname='BobbyB.Bop';
        awaittestUtils.fields.editInput($input,name);
        awaittestUtils.fields.triggerKeydown($input,'tab');

        $input=$('.o_selected_rowinput[name=age]');
        varage='22';
        awaittestUtils.fields.editInput($input,age);
        //Thisoperationcauseslist'lltrytoselectundefinedrecord.
        awaittestUtils.fields.triggerKeydown($input,'enter');

        //Checkswehavestillonly1record...
        assert.containsN(list,'.o_data_row',1,"shouldnowhave1records");
        //...andverifymodificationwasoccured.
        varnameField=list.$('td[title="'+name+'"]');
        varageField=nameField.parent().find('.o_list_number');
        assert.strictEqual(ageField.text(),age,"Theagefieldmustbeupdated");
        list.destroy();
    });

    QUnit.test('Refreshthelistonlywhenneeded',asyncfunction(assert){
        assert.expect(3);

        varrefresh_count=0;
        varlist=awaitcreateView({
            View:SingletonListView,
            model:'person',
            data:this.data,
            arch:'<treeeditable="top"js_class="singleton_list">'+
                    '<fieldname="name"/>'+
                    '<fieldname="age"/>'+
                   '</tree>',
            mockRPC:this.mockRPC,
        });
        list.realReload=list.reload;
        list.reload=function(){
            refresh_count++;
            returnthis.realReload();
        };
        //ModifyRecord
        awaittestUtils.dom.click(list.$('.o_data_row:nth-child(2)>.o_list_number'));
        var$input=$('.o_selected_rowinput[name=age]');
        awaittestUtils.fields.editInput($input,'70');
        awaittestUtils.fields.triggerKeydown($input,'enter');
        awaittestUtils.dom.click($('.o_list_button_save'));
        assert.strictEqual(refresh_count,0,"don'trefreshwheneditexistingline");

        //Addexistingrecord
        awaittestUtils.dom.click($('.o_list_button_add'));
        $input=$('.o_selected_rowinput[name=name]');
        awaittestUtils.fields.editInput($input,'LetoIIAtreides');
        awaittestUtils.fields.triggerKeydown($input,'tab');
        $input=$('.o_selected_rowinput[name=age]');
        awaittestUtils.fields.editInput($input,'800');
        awaittestUtils.dom.click($('.o_list_button_save'));
        assert.strictEqual(refresh_count,1,"refreshaftertriedtocreateanexistingrecord");

        //Addnewrecord
        awaittestUtils.dom.click($('.o_list_button_add'));
        $input=$('.o_selected_rowinput[name=name]');
        awaittestUtils.fields.editInput($input,'ValentinCognito');
        awaittestUtils.fields.triggerKeydown($input,'tab');
        $input=$('.o_selected_rowinput[name=age]');
        awaittestUtils.fields.editInput($input,'37');
        awaittestUtils.fields.triggerKeydown($input,'enter');
        awaittestUtils.dom.click($('.o_list_button_save'));
        assert.strictEqual(refresh_count,1,"don'trefreshwhencreateentirelynewrecord");

        list.destroy();
    });

    QUnit.test('Workingroupedlist',asyncfunction(assert){
        assert.expect(6);

        varrefresh_count=0;
        varlist=awaitcreateView({
            View:SingletonListView,
            model:'person',
            data:this.data,
            arch:'<treeeditable="top"js_class="singleton_list">'+
                    '<fieldname="name"/>'+
                    '<fieldname="age"/>'+
                    '<fieldname="job"/>'+
                   '</tree>',
            mockRPC:this.mockRPC,
            groupBy:['job'],
        });
        list.realReload=list.reload;
        list.reload=function(){
            refresh_count++;
            returnthis.realReload();
        };
        //Opens'Professor'group
        awaittestUtils.dom.click(list.$('.o_group_header:nth-child(2)'));

        //Createsanewrecord...
        awaittestUtils.dom.click(list.$('.o_add_record_rowa'));
        var$input=$('.o_selected_rowinput[name=name]');
        awaittestUtils.fields.editInput($input,'DelTutorial');
        awaittestUtils.fields.triggerKeydown($input,'tab');
        $input=$('.o_selected_rowinput[name=age]');
        awaittestUtils.fields.editInput($input,'32');
        awaittestUtils.fields.triggerKeydown($input,'tab');
        awaittestUtils.dom.click($('.o_list_button_save'));
        //...thenchecksthelistdidn'trefresh
        assert.strictEqual(refresh_count,0,
            "don'trefreshwhencreatingnewrecord");

        //Createsanexistingrecordinsamegroup...
        awaittestUtils.dom.click(list.$('.o_add_record_rowa'));
        var$input=$('.o_selected_rowinput[name=name]');
        awaittestUtils.fields.editInput($input,'SamuelOak');
        awaittestUtils.dom.click($('.o_list_button_save'));
        //...thenchecksthelisthasbeenrefreshed
        assert.strictEqual(refresh_count,1,
            "refreshwhentrytocreateanexistingrecord");

        //Createsanexistingbutnotdisplayedrecord...
        awaittestUtils.dom.click(list.$('.o_add_record_rowa'));
        var$input=$('.o_selected_rowinput[name=name]');
        awaittestUtils.fields.editInput($input,'DanielFortesque');
        awaittestUtils.fields.triggerKeydown($input,'tab');
        $input=$('.o_selected_rowinput[name=age]');
        awaittestUtils.fields.editInput($input,'55');
        awaittestUtils.fields.triggerKeydown($input,'tab');
        $input=$('.o_selected_rowinput[name=job]');
        awaittestUtils.fields.editInput($input,'Soldier');
        awaittestUtils.dom.click($('.o_list_button_save'));
        //..thenchecksthelistdidn'trefresh
        assert.strictEqual(refresh_count,1,
            "don'trefreshwhencreatinganexistingrecordbutthisrecord"+
            "isn'tpresentintheview");

        //Opens'Soldier'group
        awaittestUtils.dom.click(list.$('.o_group_header:nth-child(1)').first());
        //Checkstherecordhasbeencorrectlyupdated
        varageCell=$('tr.o_data_rowtd.o_list_number').first();
        assert.strictEqual(ageCell.text(),"55",
            "ageoftherecordmustbeupdated");
        //Editsthefreshlycreatedrecord...
        awaittestUtils.dom.click(list.$('tr.o_data_rowtd.o_list_number').eq(1));
        $input=$('.o_selected_rowinput[name=age]');
        awaittestUtils.fields.editInput($input,'66');
        awaittestUtils.dom.click($('.o_list_button_save'));
        //...thenchecksthelistanddatahavebeenrefreshed
        assert.strictEqual(refresh_count,2,
            "refreshwhentrytocreateanexistingrecordpresentintheview");
        ageCell=$('tr.o_data_rowtd.o_list_number').first();
        assert.strictEqual(ageCell.text(),"66",
            "ageoftherecordmustbeupdated");

        list.destroy();
    });
});

});
