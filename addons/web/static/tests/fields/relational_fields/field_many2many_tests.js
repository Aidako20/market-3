flectra.define('web.field_many_to_many_tests',function(require){
"usestrict";

varFormView=require('web.FormView');
vartestUtils=require('web.test_utils');

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
                        int_field:{string:"int_field",type:"integer",sortable:true},
                        turtles:{string:"one2manyturtlefield",type:"one2many",relation:'turtle',relation_field:'turtle_trululu'},
                        timmy:{string:"pokemon",type:"many2many",relation:'partner_type'},
                        color:{
                            type:"selection",
                            selection:[['red',"Red"],['black',"Black"]],
                            default:'red',
                            string:"Color",
                        },
                        user_id:{string:"User",type:'many2one',relation:'user'},
                        reference:{
                            string:"ReferenceField",type:'reference',selection:[
                                ["product","Product"],["partner_type","PartnerType"],["partner","Partner"]]
                        },
                    },
                    records:[{
                        id:1,
                        display_name:"firstrecord",
                        foo:"yop",
                        int_field:10,
                        turtles:[2],
                        timmy:[],
                        user_id:17,
                        reference:'product,37',
                    },{
                        id:2,
                        display_name:"secondrecord",
                        foo:"blip",
                        int_field:9,
                        timmy:[],
                        user_id:17,
                    },{
                        id:4,
                        display_name:"aaa",
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
                        partner_ids:{string:"Partner",type:"many2many",relation:'partner'},
                    },
                    records:[{
                        id:1,
                        display_name:"leonardo",
                        turtle_foo:"yop",
                        partner_ids:[],
                    },{
                        id:2,
                        display_name:"donatello",
                        turtle_foo:"blip",
                        partner_ids:[2,4],
                    },{
                        id:3,
                        display_name:"raphael",
                        turtle_foo:"kawa",
                        partner_ids:[],
                    }],
                    onchanges:{},
                },
                user:{
                    fields:{
                        name:{string:"Name",type:"char"},
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
        },
    },function(){
        QUnit.module('FieldMany2Many');

        QUnit.test('many2manykanban:edition',asyncfunction(assert){
            assert.expect(33);

            this.data.partner.records[0].timmy=[12,14];
            this.data.partner_type.records.push({id:15,display_name:"red",color:6});
            this.data.partner_type.records.push({id:18,display_name:"yellow",color:4});
            this.data.partner_type.records.push({id:21,display_name:"blue",color:1});

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<fieldname="timmy">'+
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
                    '<formstring="Partners">'+
                    '<fieldname="display_name"/>'+
                    '</form>'+
                    '</field>'+
                    '</form>',
                archs:{
                    'partner_type,false,form':'<formstring="Types"><fieldname="display_name"/></form>',
                    'partner_type,false,list':'<treestring="Types"><fieldname="display_name"/></tree>',
                    'partner_type,false,search':'<searchstring="Types">'+
                        '<fieldname="name"string="Name"/>'+
                        '</search>',
                },
                res_id:1,
                mockRPC:function(route,args){
                    if(route==='/web/dataset/call_kw/partner_type/write'){
                        assert.strictEqual(args.args[1].display_name,"newname","shouldwrite'new_name'");
                    }
                    if(route==='/web/dataset/call_kw/partner_type/create'){
                        assert.strictEqual(args.args[0].display_name,"Anewtype","shouldcreate'Anewtype'");
                    }
                    if(route==='/web/dataset/call_kw/partner/write'){
                        varcommands=args.args[1].timmy;
                        assert.strictEqual(commands.length,1,"shouldhavegeneratedonecommand");
                        assert.strictEqual(commands[0][0],6,"generatedcommandshouldbeREPLACEWITH");
                        //getthecreatedtype'sid
                        varcreatedType=_.findWhere(this.data.partner_type.records,{
                            display_name:"Anewtype"
                        });
                        varids=_.sortBy([12,15,18].concat(createdType.id),_.identity.bind(_));
                        assert.ok(_.isEqual(_.sortBy(commands[0][2],_.identity.bind(_)),ids),
                            "newvalueshouldbe"+ids);
                    }
                    returnthis._super.apply(this,arguments);
                },
            });

            //theSelectCreateDialogrequeststhesession,sointerceptitscustom
            //eventtospecifyafakesessiontopreventitfromcrashing
            testUtils.mock.intercept(form,'get_session',function(event){
                event.data.callback({user_context:{}});
            });

            assert.ok(!form.$('.o_kanban_view.delete_icon').length,
                'deleteiconshouldnotbevisibleinreadonly');
            assert.ok(!form.$('.o_field_many2many.o-kanban-button-new').length,
                '"Add"buttonshouldnotbevisibleinreadonly');

            awaittestUtils.form.clickEdit(form);

            assert.strictEqual(form.$('.o_kanban_record:not(.o_kanban_ghost)').length,2,
                'shouldcontain2records');
            assert.strictEqual(form.$('.o_kanban_record:first()span').text(),'gold',
                'display_nameofsubrecordshouldbetheoneinDB');
            assert.ok(form.$('.o_kanban_view.delete_icon').length,
                'deleteiconshouldbevisibleinedit');
            assert.ok(form.$('.o_field_many2many.o-kanban-button-new').length,
                '"Add"buttonshouldbevisibleinedit');
            assert.strictEqual(form.$('.o_field_many2many.o-kanban-button-new').text().trim(),"Add",
                'Createbuttonshouldhave"Add"label');

            //editexistingsubrecord
            awaittestUtils.dom.click(form.$('.oe_kanban_global_click:first()'));

            awaittestUtils.fields.editInput($('.modal.o_form_viewinput'),'newname');
            awaittestUtils.dom.click($('.modal.modal-footer.btn-primary'));
            assert.strictEqual(form.$('.o_kanban_record:first()span').text(),'newname',
                'valueofsubrecordshouldhavebeenupdated');

            //addsubrecords
            //->singleselect
            awaittestUtils.dom.click(form.$('.o_field_many2many.o-kanban-button-new'));
            assert.ok($('.modal.o_list_view').length,"shouldhaveopenedalistviewinamodal");
            assert.strictEqual($('.modal.o_list_viewtbody.o_list_record_selector').length,3,
                "listviewshouldcontain3records");
            awaittestUtils.dom.click($('.modal.o_list_viewtbodytr:contains(red)'));
            assert.ok(!$('.modal.o_list_view').length,"shouldhaveclosedthemodal");
            assert.strictEqual(form.$('.o_kanban_record:not(.o_kanban_ghost)').length,3,
                'kanbanshouldnowcontain3records');
            assert.ok(form.$('.o_kanban_record:contains(red)').length,
                'record"red"shouldbeinthekanban');

            //->multipleselect
            awaittestUtils.dom.click(form.$('.o_field_many2many.o-kanban-button-new'));
            assert.ok($('.modal.o_select_button').prop('disabled'),"selectbuttonshouldbedisabled");
            assert.strictEqual($('.modal.o_list_viewtbody.o_list_record_selector').length,2,
                "listviewshouldcontain2records");
            awaittestUtils.dom.click($('.modal.o_list_viewthead.o_list_record_selectorinput'));
            awaittestUtils.dom.click($('.modal.o_select_button'));
            assert.ok(!$('.modal.o_select_button').prop('disabled'),"selectbuttonshouldbeenabled");
            assert.ok(!$('.modal.o_list_view').length,"shouldhaveclosedthemodal");
            assert.strictEqual(form.$('.o_kanban_record:not(.o_kanban_ghost)').length,5,
                'kanbanshouldnowcontain5records');
            //->createdrecord
            awaittestUtils.dom.click(form.$('.o_field_many2many.o-kanban-button-new'));
            awaittestUtils.dom.click($('.modal.modal-footer.btn-primary:nth(1)'));
            assert.ok($('.modal.o_form_view.o_form_editable').length,
                "shouldhaveopenedaformviewineditmode,inamodal");
            awaittestUtils.fields.editInput($('.modal.o_form_viewinput'),'Anewtype');
            awaittestUtils.dom.click($('.modal:nth(1)footer.btn-primary:first()'));
            assert.ok(!$('.modal').length,"shouldhaveclosedbothmodals");
            assert.strictEqual(form.$('.o_kanban_record:not(.o_kanban_ghost)').length,6,
                'kanbanshouldnowcontain6records');
            assert.ok(form.$('.o_kanban_record:contains(Anewtype)').length,
                'thenewlycreatedtypeshouldbeinthekanban');

            //deletesubrecords
            awaittestUtils.dom.click(form.$('.o_kanban_record:contains(silver)'));
            assert.strictEqual($('.modal.modal-footer.o_btn_remove').length,1,
                'ThereshouldbeamodalhavingRemoveButton');
            awaittestUtils.dom.click($('.modal.modal-footer.o_btn_remove'));
            assert.containsNone($('.o_modal'),"modalshouldhavebeenclosed");
            assert.strictEqual(form.$('.o_kanban_record:not(.o_kanban_ghost)').length,5,
                'shouldcontain5records');
            assert.ok(!form.$('.o_kanban_record:contains(silver)').length,
                'theremovedrecordshouldnotbeinkanbananymore');

            awaittestUtils.dom.click(form.$('.o_kanban_record:contains(blue).delete_icon'));
            assert.strictEqual(form.$('.o_kanban_record:not(.o_kanban_ghost)').length,4,
                'shouldcontain4records');
            assert.ok(!form.$('.o_kanban_record:contains(blue)').length,
                'theremovedrecordshouldnotbeinkanbananymore');

            //savetherecord
            awaittestUtils.form.clickSave(form);
            form.destroy();
        });

        QUnit.test('many2manykanban(editable):properlyhandlecreate_textnodeoption',asyncfunction(assert){
            assert.expect(1);

            this.data.partner.records[0].timmy=[12];

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<fieldname="timmy"options="{\'create_text\':\'Addtimmy\'}"mode="kanban">'+
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
            assert.strictEqual(form.$('.o_field_many2many[name="timmy"].o-kanban-button-new').text().trim(),
                "Addtimmy","InM2MKanban,Addbuttonshouldhave'Addtimmy'label");

            form.destroy();
        });

        QUnit.test('many2manykanban:createactiondisabled',asyncfunction(assert){
            assert.expect(4);

            this.data.partner.records[0].timmy=[12,14];

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<fieldname="timmy">'+
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
                archs:{
                    'partner_type,false,list':'<tree><fieldname="name"/></tree>',
                    'partner_type,false,search':'<search>'+
                        '<fieldname="display_name"string="Name"/>'+
                        '</search>',
                },
                res_id:1,
                session:{user_context:{}},
            });

            assert.ok(!form.$('.o-kanban-button-new').length,
                '"Add"buttonshouldnotbeavailableinreadonly');

            awaittestUtils.form.clickEdit(form);

            assert.ok(form.$('.o-kanban-button-new').length,
                '"Add"buttonshouldbeavailableinedit');
            assert.ok(form.$('.o_kanban_view.delete_icon').length,
                'deleteiconshouldbevisibleinedit');

            awaittestUtils.dom.click(form.$('.o-kanban-button-new'));
            assert.strictEqual($('.modal.modal-footer.btn-primary').length,1,//onlybutton'Select'
                '"Create"buttonshouldnotbeavailableinthemodal');

            form.destroy();
        });

        QUnit.test('many2manykanban:conditionalcreate/deleteactions',asyncfunction(assert){
            assert.expect(6);

            this.data.partner.records[0].timmy=[12,14];

            constform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:`
                    <form>
                        <fieldname="color"/>
                        <fieldname="timmy"options="{'create':[('color','=','red')],'delete':[('color','=','red')]}">
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
                        </field>
                    </form>`,
                archs:{
                    'partner_type,false,form':'<form><fieldname="name"/></form>',
                    'partner_type,false,list':'<tree><fieldname="name"/></tree>',
                    'partner_type,false,search':'<search/>',
                },
                res_id:1,
                viewOptions:{
                    mode:'edit',
                },
            });

            //colorisred
            assert.containsOnce(form,'.o-kanban-button-new','"Add"buttonshouldbeavailable');

            awaittestUtils.dom.click(form.$('.o_kanban_record:contains(silver)'));
            assert.containsOnce(document.body,'.modal.modal-footer.o_btn_remove',
                'removebuttonshouldbevisibleinmodal');
            awaittestUtils.dom.click($('.modal.modal-footer.o_form_button_cancel'));

            awaittestUtils.dom.click(form.$('.o-kanban-button-new'));
            assert.containsN(document.body,'.modal.modal-footerbutton',3,
                'thereshouldbe3buttonsavailableinthemodal');
            awaittestUtils.dom.click($('.modal.modal-footer.o_form_button_cancel'));

            //setcolortoblack
            awaittestUtils.fields.editSelect(form.$('select[name="color"]'),'"black"');
            assert.containsOnce(form,'.o-kanban-button-new',
                '"Add"buttonshouldstillbeavailableevenaftercolorfieldchanged');

            awaittestUtils.dom.click(form.$('.o-kanban-button-new'));
            //onlyselectandcancelbuttonshouldbeavailable,create
            //buttonshouldberemovedbasedoncolorfieldcondition
            assert.containsN(document.body,'.modal.modal-footerbutton',2,
                '"Create"buttonshouldnotbeavailableinthemodalaftercolorfieldchanged');
            awaittestUtils.dom.click($('.modal.modal-footer.o_form_button_cancel'));

            awaittestUtils.dom.click(form.$('.o_kanban_record:contains(silver)'));
            assert.containsNone(document.body,'.modal.modal-footer.o_btn_remove',
                'removebuttonshouldbevisibleinmodal');

            form.destroy();
        });

        QUnit.test('many2manylist(noneditable):edition',asyncfunction(assert){
            assert.expect(29);

            this.data.partner.records[0].timmy=[12,14];
            this.data.partner_type.records.push({id:15,display_name:"bronze",color:6});
            this.data.partner_type.fields.float_field={string:'Float',type:'float'};
            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<fieldname="timmy">'+
                    '<tree>'+
                    '<fieldname="display_name"/><fieldname="float_field"/>'+
                    '</tree>'+
                    '<formstring="Partners">'+
                    '<fieldname="display_name"/>'+
                    '</form>'+
                    '</field>'+
                    '</form>',
                archs:{
                    'partner_type,false,list':'<tree><fieldname="display_name"/></tree>',
                    'partner_type,false,search':'<search><fieldname="display_name"/></search>',
                },
                res_id:1,
                mockRPC:function(route,args){
                    if(args.method!=='load_views'){
                        assert.step(_.last(route.split('/')));
                    }
                    if(args.method==='write'&&args.model==='partner'){
                        assert.deepEqual(args.args[1].timmy,[
                            [6,false,[12,15]],
                        ]);
                    }
                    returnthis._super.apply(this,arguments);
                },
            });
            assert.containsNone(form.$('.o_list_record_remove'),
                'deleteiconshouldnotbevisibleinreadonly');
            assert.containsNone(form.$('.o_field_x2many_list_row_add'),
                '"Addanitem"shouldnotbevisibleinreadonly');

            awaittestUtils.form.clickEdit(form);

            assert.containsN(form,'.o_list_viewtd.o_list_number',2,
                'shouldcontain2records');
            assert.strictEqual(form.$('.o_list_viewtbodytd:first()').text(),'gold',
                'display_nameoffirstsubrecordshouldbetheoneinDB');
            assert.ok(form.$('.o_list_record_remove').length,
                'deleteiconshouldbevisibleinedit');
            assert.ok(form.$('.o_field_x2many_list_row_add').length,
                '"Addanitem"shouldbevisibleinedit');

            //editexistingsubrecord
            awaittestUtils.dom.click(form.$('.o_list_viewtbodytr:first()'));

            assert.containsNone($('.modal.modal-footer.o_btn_remove'),
                'thereshouldnotbea"Remove"buttoninthemodalfooter');

            awaittestUtils.fields.editInput($('.modal.o_form_viewinput'),'newname');
            awaittestUtils.dom.click($('.modal.modal-footer.btn-primary'));
            assert.strictEqual(form.$('.o_list_viewtbodytd:first()').text(),'newname',
                'valueofsubrecordshouldhavebeenupdated');

            //addnewsubrecords
            awaittestUtils.dom.click(form.$('.o_field_x2many_list_row_adda'));
            assert.containsNone($('.modal.modal-footer.o_btn_remove'),
                'thereshouldnotbea"Remove"buttoninthemodalfooter');
            assert.strictEqual($('.modal.o_list_view').length,1,
                "amodalshouldbeopen");
            assert.strictEqual($('.modal.o_list_view.o_data_row').length,1,
                "thelistshouldcontainonerow");
            awaittestUtils.dom.click($('.modal.o_list_view.o_data_row'));
            assert.strictEqual($('.modal.o_list_view').length,0,
                "themodalshouldbeclosed");
            assert.containsN(form,'.o_list_viewtd.o_list_number',3,
                'shouldcontain3subrecords');

            //removesubrecords
            awaittestUtils.dom.click(form.$('.o_list_record_remove:nth(1)'));
            assert.containsN(form,'.o_list_viewtd.o_list_number',2,
                'shouldcontain2subrecords');
            assert.strictEqual(form.$('.o_list_view.o_data_rowtd:first').text(),'newname',
                'theupdatedrowstillhasthecorrectvalues');

            //save
            awaittestUtils.form.clickSave(form);
            assert.containsN(form,'.o_list_viewtd.o_list_number',2,
                'shouldcontain2subrecords');
            assert.strictEqual(form.$('.o_list_view.o_data_rowtd:first').text(),
                'newname','theupdatedrowstillhasthecorrectvalues');

            assert.verifySteps([
                'read',//mainrecord
                'read',//relationalfield
                'read',//relationalrecordindialog
                'write',//saverelationalrecordfromdialog
                'read',//relationalfield(updated)
                'search_read',//listviewindialog
                'read',//relationalfield(updated)
                'write',//savemainrecord
                'read',//mainrecord
                'read',//relationalfield
            ]);

            form.destroy();
        });

        QUnit.test('many2manylist(editable):edition',asyncfunction(assert){
            assert.expect(31);

            this.data.partner.records[0].timmy=[12,14];
            this.data.partner_type.records.push({id:15,display_name:"bronze",color:6});
            this.data.partner_type.fields.float_field={string:'Float',type:'float'};
            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<fieldname="timmy">'+
                    '<treeeditable="top">'+
                    '<fieldname="display_name"/><fieldname="float_field"/>'+
                    '</tree>'+
                    '</field>'+
                    '</form>',
                archs:{
                    'partner_type,false,list':'<tree><fieldname="display_name"/></tree>',
                    'partner_type,false,search':'<search><fieldname="display_name"/></search>',
                },
                mockRPC:function(route,args){
                    if(args.method!=='load_views'){
                        assert.step(_.last(route.split('/')));
                    }
                    if(args.method==='write'){
                        assert.deepEqual(args.args[1].timmy,[
                            [6,false,[12,15]],
                            [1,12,{display_name:'newname'}],
                        ]);
                    }
                    returnthis._super.apply(this,arguments);
                },
                res_id:1,
            });

            assert.ok(!form.$('.o_list_record_remove').length,
                'deleteiconshouldnotbevisibleinreadonly');
            assert.ok(!form.$('.o_field_x2many_list_row_add').length,
                '"Addanitem"shouldnotbevisibleinreadonly');

            awaittestUtils.form.clickEdit(form);

            assert.containsN(form,'.o_list_viewtd.o_list_number',2,
                'shouldcontain2records');
            assert.strictEqual(form.$('.o_list_viewtbodytd:first()').text(),'gold',
                'display_nameoffirstsubrecordshouldbetheoneinDB');
            assert.ok(form.$('.o_list_record_remove').length,
                'deleteiconshouldbevisibleinedit');
            assert.hasClass(form.$('td.o_list_record_removebutton').first(),'fafa-times',
                "shouldhaveXiconstoremove(unlink)records");
            assert.ok(form.$('.o_field_x2many_list_row_add').length,
                '"Addanitem"shouldnotvisibleinedit');

            //editexistingsubrecord
            awaittestUtils.dom.click(form.$('.o_list_viewtbodytd:first()'));
            assert.ok(!$('.modal').length,
                'inedit,clickingonasubrecordshouldnotopenadialog');
            assert.hasClass(form.$('.o_list_viewtbodytr:first()'),'o_selected_row',
                'firstrowshouldbeinedition');
            awaittestUtils.fields.editInput(form.$('.o_list_viewinput:first()'),'newname');
            assert.hasClass(form.$('.o_list_view.o_data_row:first'),'o_selected_row',
                'firstrowshouldstillbeinedition');
            assert.strictEqual(form.$('.o_list_viewinput[name=display_name]').get(0),
                document.activeElement,'editedfieldshouldstillhavethefocus');
            awaittestUtils.dom.click(form.$el);
            assert.doesNotHaveClass(form.$('.o_list_viewtbodytr:first'),'o_selected_row',
                'firstrowshouldnotbeineditionanymore');
            assert.strictEqual(form.$('.o_list_viewtbodytd:first()').text(),'newname',
                'valueofsubrecordshouldhavebeenupdated');
            assert.verifySteps(['read','read']);

            //addnewsubrecords
            awaittestUtils.dom.click(form.$('.o_field_x2many_list_row_adda'));
            assert.strictEqual($('.modal.o_list_view').length,1,
                "amodalshouldbeopen");
            assert.strictEqual($('.modal.o_list_view.o_data_row').length,1,
                "thelistshouldcontainonerow");
            awaittestUtils.dom.click($('.modal.o_list_view.o_data_row'));
            assert.strictEqual($('.modal.o_list_view').length,0,
                "themodalshouldbeclosed");
            assert.containsN(form,'.o_list_viewtd.o_list_number',3,
                'shouldcontain3subrecords');

            //removesubrecords
            awaittestUtils.dom.click(form.$('.o_list_record_remove:nth(1)'));
            assert.containsN(form,'.o_list_viewtd.o_list_number',2,
                'shouldcontain2subrecord');
            assert.strictEqual(form.$('.o_list_viewtbody.o_data_rowtd:first').text(),
                'newname','theupdatedrowstillhasthecorrectvalues');

            //save
            awaittestUtils.form.clickSave(form);
            assert.containsN(form,'.o_list_viewtd.o_list_number',2,
                'shouldcontain2subrecords');
            assert.strictEqual(form.$('.o_list_view.o_data_rowtd:first').text(),
                'newname','theupdatedrowstillhasthecorrectvalues');

            assert.verifySteps([
                'search_read',//listviewindialog
                'read',//relationalfield(updated)
                'write',//savemainrecord
                'read',//mainrecord
                'read',//relationalfield
            ]);

            form.destroy();
        });

        QUnit.test('many2many:create&deleteattributes',asyncfunction(assert){
            assert.expect(4);

            this.data.partner.records[0].timmy=[12,14];

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<fieldname="timmy">'+
                    '<treecreate="true"delete="true">'+
                    '<fieldname="color"/>'+
                    '</tree>'+
                    '</field>'+
                    '</form>',
                res_id:1,
            });

            awaittestUtils.form.clickEdit(form);

            assert.containsOnce(form,'.o_field_x2many_list_row_add',"shouldhavethe'Addanitem'link");
            assert.containsN(form,'.o_list_record_remove',2,"shouldhavethe'Addanitem'link");

            form.destroy();

            form=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<fieldname="timmy">'+
                    '<treecreate="false"delete="false">'+
                    '<fieldname="color"/>'+
                    '</tree>'+
                    '</field>'+
                    '</form>',
                res_id:1,
            });

            awaittestUtils.form.clickEdit(form);

            assert.containsOnce(form,'.o_field_x2many_list_row_add',"shouldhavethe'Addanitem'link");
            assert.containsN(form,'.o_list_record_remove',2,"eachrecordshouldhavethe'RemoveItem'link");

            form.destroy();
        });

        QUnit.test('many2manylist:createactiondisabled',asyncfunction(assert){
            assert.expect(2);
            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<fieldname="timmy">'+
                    '<treecreate="0">'+
                    '<fieldname="name"/>'+
                    '</tree>'+
                    '</field>'+
                    '</form>',
                res_id:1,
            });

            assert.containsNone(form,'.o_field_x2many_list_row_add',
                '"Addanitem"linkshouldnotbeavailableinreadonly');

            awaittestUtils.form.clickEdit(form);

            assert.containsOnce(form,'.o_field_x2many_list_row_add',
                '"Addanitem"linkshouldbeavailableinedit');

            form.destroy();
        });

        QUnit.test('fieldmany2manylistcomodelnotwritable',asyncfunction(assert){
            /**
             *Many2ManyListshouldbehaveasthem2m_tags
             *thatis,therelationcanbealteredevenifthecomodelitselfisnotCRUD-able
             *Thiscanhappenwhensomeonehasreadaccessaloneonthecomodel
             *andfullCRUDonthecurrentmodel
             */
            assert.expect(12);

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:`<formstring="Partners">
                        <fieldname="timmy"widget="many2many"can_create="false"can_write="false"/>
                    </form>`,
                archs:{
                    'partner_type,false,list':`<treecreate="false"delete="false"edit="false">
                                                    <fieldname="display_name"/>
                                                </tree>`,
                    'partner_type,false,search':'<search><fieldname="display_name"/></search>',
                },
                mockRPC:function(route,args){
                    if(route==='/web/dataset/call_kw/partner/create'){
                        assert.deepEqual(args.args[0],{timmy:[[6,false,[12]]]});
                    }
                    if(route==='/web/dataset/call_kw/partner/write'){
                        assert.deepEqual(args.args[1],{timmy:[[6,false,[]]]});
                    }
                    returnthis._super.apply(this,arguments);
                }
            });

            assert.containsOnce(form,'.o_field_many2many.o_field_x2many_list_row_add');
            awaittestUtils.dom.click(form.$('.o_field_many2many.o_field_x2many_list_row_adda'));
            assert.containsOnce(document.body,'.modal');

            assert.containsN($('.modal-footer'),'button',2);
            assert.containsOnce($('.modal-footer'),'button.o_select_button');
            assert.containsOnce($('.modal-footer'),'button.o_form_button_cancel');

            awaittestUtils.dom.click($('.modal.o_list_view.o_data_cell:first()'));
            assert.containsNone(document.body,'.modal');

            assert.containsOnce(form,'.o_field_many2many.o_data_row');
            assert.equal($('.o_field_many2many.o_data_row').text(),'gold');
            assert.containsOnce(form,'.o_field_many2many.o_field_x2many_list_row_add');

            awaittestUtils.form.clickSave(form);
            awaittestUtils.form.clickEdit(form);

            assert.containsOnce(form,'.o_field_many2many.o_data_row.o_list_record_remove');
            awaittestUtils.dom.click(form.$('.o_field_many2many.o_data_row.o_list_record_remove'));
            awaittestUtils.form.clickSave(form);

            form.destroy();
        });

        QUnit.test('many2manylist:conditionalcreate/deleteactions',asyncfunction(assert){
            assert.expect(6);

            this.data.partner.records[0].timmy=[12,14];

            constform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:`
                    <form>
                        <fieldname="color"/>
                        <fieldname="timmy"options="{'create':[('color','=','red')],'delete':[('color','=','red')]}">
                            <tree>
                                <fieldname="name"/>
                            </tree>
                        </field>
                    </form>`,
                archs:{
                    'partner_type,false,list':'<tree><fieldname="name"/></tree>',
                    'partner_type,false,search':'<search/>',
                },
                res_id:1,
                viewOptions:{
                    mode:'edit',
                },
            });

            //colorisred->createanddeleteactionsareavailable
            assert.containsOnce(form,'.o_field_x2many_list_row_add',
                "shouldhavethe'Addanitem'link");
            assert.containsN(form,'.o_list_record_remove',2,
                "shouldhavetworemoveicons");

            awaittestUtils.dom.click(form.$('.o_field_x2many_list_row_adda'));

            assert.containsN(document.body,'.modal.modal-footerbutton',3,
                'thereshouldbe3buttonsavailableinthemodal');

            awaittestUtils.dom.click($('.modal.modal-footer.o_form_button_cancel'));

            //setcolortoblack->createanddeleteactionsarenolongeravailable
            awaittestUtils.fields.editSelect(form.$('select[name="color"]'),'"black"');

            //addalineandremoveiconshouldstillbethereastheydon'tcreate/deleterecords,
            //butratheradd/removelinks
            assert.containsOnce(form,'.o_field_x2many_list_row_add',
                '"Addaline"buttonshouldstillbeavailableevenaftercolorfieldchanged');
            assert.containsN(form,'.o_list_record_remove',2,
                "shouldstillhaveremoveiconevenaftercolorfieldchanged");

            awaittestUtils.dom.click(form.$('.o_field_x2many_list_row_adda'));
            assert.containsN(document.body,'.modal.modal-footerbutton',2,
                '"Create"buttonshouldnotbeavailableinthemodalaftercolorfieldchanged');

            form.destroy();
        });

        QUnit.test('many2manyfieldwithlink/unlinkoptions(list)',asyncfunction(assert){
            assert.expect(5);

            this.data.partner.records[0].timmy=[12,14];

            constform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:`
                    <form>
                        <fieldname="color"/>
                        <fieldname="timmy"options="{'link':[('color','=','red')],'unlink':[('color','=','red')]}">
                            <tree>
                                <fieldname="name"/>
                            </tree>
                        </field>
                    </form>`,
                archs:{
                    'partner_type,false,list':'<tree><fieldname="name"/></tree>',
                    'partner_type,false,search':'<search/>',
                },
                res_id:1,
                viewOptions:{
                    mode:'edit',
                },
            });

            //colorisred->linkandunlinkactionsareavailable
            assert.containsOnce(form,'.o_field_x2many_list_row_add',
                "shouldhavethe'Addanitem'link");
            assert.containsN(form,'.o_list_record_remove',2,
                "shouldhavetworemoveicons");

            awaittestUtils.dom.click(form.$('.o_field_x2many_list_row_adda'));

            assert.containsN(document.body,'.modal.modal-footerbutton',3,
                'thereshouldbe3buttonsavailableinthemodal(Createactionisavailable)');

            awaittestUtils.dom.click($('.modal.modal-footer.o_form_button_cancel'));

            //setcolortoblack->linkandunlinkactionsarenolongeravailable
            awaittestUtils.fields.editSelect(form.$('select[name="color"]'),'"black"');

            assert.containsNone(form,'.o_field_x2many_list_row_add',
                '"Addaline"shouldnolongerbeavailableaftercolorfieldchanged');
            assert.containsNone(form,'.o_list_record_remove',
                "shouldnolongerhaveremoveiconaftercolorfieldchanged");

            form.destroy();
        });

        QUnit.test('many2manyfieldwithlink/unlinkoptions(list,create="0")',asyncfunction(assert){
            assert.expect(5);

            this.data.partner.records[0].timmy=[12,14];

            constform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:`
                    <form>
                        <fieldname="color"/>
                        <fieldname="timmy"options="{'link':[('color','=','red')],'unlink':[('color','=','red')]}">
                            <treecreate="0">
                                <fieldname="name"/>
                            </tree>
                        </field>
                    </form>`,
                archs:{
                    'partner_type,false,list':'<tree><fieldname="name"/></tree>',
                    'partner_type,false,search':'<search/>',
                },
                res_id:1,
                viewOptions:{
                    mode:'edit',
                },
            });

            //colorisred->linkandunlinkactionsareavailable
            assert.containsOnce(form,'.o_field_x2many_list_row_add',
                "shouldhavethe'Addanitem'link");
            assert.containsN(form,'.o_list_record_remove',2,
                "shouldhavetworemoveicons");

            awaittestUtils.dom.click(form.$('.o_field_x2many_list_row_adda'));

            assert.containsN(document.body,'.modal.modal-footerbutton',2,
                'thereshouldbe2buttonsavailableinthemodal(Createactionisnotavailable)');

            awaittestUtils.dom.click($('.modal.modal-footer.o_form_button_cancel'));

            //setcolortoblack->linkandunlinkactionsarenolongeravailable
            awaittestUtils.fields.editSelect(form.$('select[name="color"]'),'"black"');

            assert.containsNone(form,'.o_field_x2many_list_row_add',
                '"Addaline"shouldnolongerbeavailableaftercolorfieldchanged');
            assert.containsNone(form,'.o_list_record_remove',
                "shouldnolongerhaveremoveiconaftercolorfieldchanged");

            form.destroy();
        });

        QUnit.test('many2manyfieldwithlinkoption(kanban)',asyncfunction(assert){
            assert.expect(3);

            this.data.partner.records[0].timmy=[12,14];

            constform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:`
                    <form>
                        <fieldname="color"/>
                        <fieldname="timmy"options="{'link':[('color','=','red')]}">
                            <kanban>
                                <templates>
                                    <tt-name="kanban-box">
                                        <div><fieldname="name"/></div>
                                    </t>
                                </templates>
                            </kanban>
                        </field>
                    </form>`,
                archs:{
                    'partner_type,false,list':'<tree><fieldname="name"/></tree>',
                    'partner_type,false,search':'<search/>',
                },
                res_id:1,
                viewOptions:{
                    mode:'edit',
                },
            });

            //colorisred->linkandunlinkactionsareavailable
            assert.containsOnce(form,'.o-kanban-button-new',"shouldhavethe'Add'button");

            awaittestUtils.dom.click(form.$('.o-kanban-button-new'));

            assert.containsN(document.body,'.modal.modal-footerbutton',3,
                'thereshouldbe3buttonsavailableinthemodal(Createactionisavailable');

            awaittestUtils.dom.click($('.modal.modal-footer.o_form_button_cancel'));

            //setcolortoblack->linkandunlinkactionsarenolongeravailable
            awaittestUtils.fields.editSelect(form.$('select[name="color"]'),'"black"');

            assert.containsNone(form,'.o-kanban-button-new',
                '"Add"shouldnolongerbeavailableaftercolorfieldchanged');

            form.destroy();
        });

        QUnit.test('many2manyfieldwithlinkoption(kanban,create="0")',asyncfunction(assert){
            assert.expect(3);

            this.data.partner.records[0].timmy=[12,14];

            constform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:`
                    <form>
                        <fieldname="color"/>
                        <fieldname="timmy"options="{'link':[('color','=','red')]}">
                            <kanbancreate="0">
                                <templates>
                                    <tt-name="kanban-box">
                                        <div><fieldname="name"/></div>
                                    </t>
                                </templates>
                            </kanban>
                        </field>
                    </form>`,
                archs:{
                    'partner_type,false,list':'<tree><fieldname="name"/></tree>',
                    'partner_type,false,search':'<search/>',
                },
                res_id:1,
                viewOptions:{
                    mode:'edit',
                },
            });

            //colorisred->linkandunlinkactionsareavailable
            assert.containsOnce(form,'.o-kanban-button-new',"shouldhavethe'Add'button");

            awaittestUtils.dom.click(form.$('.o-kanban-button-new'));

            assert.containsN(document.body,'.modal.modal-footerbutton',2,
                'thereshouldbe2buttonsavailableinthemodal(Createactionisnotavailable');

            awaittestUtils.dom.click($('.modal.modal-footer.o_form_button_cancel'));

            //setcolortoblack->linkandunlinkactionsarenolongeravailable
            awaittestUtils.fields.editSelect(form.$('select[name="color"]'),'"black"');

            assert.containsNone(form,'.o-kanban-button-new',
                '"Add"shouldnolongerbeavailableaftercolorfieldchanged');

            form.destroy();
        });

        QUnit.test('many2manylist:listofidasdefaultvalue',asyncfunction(assert){
            assert.expect(1);

            this.data.partner.fields.turtles.default=[2,3];
            this.data.partner.fields.turtles.type="many2many";

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<fieldname="turtles">'+
                    '<tree>'+
                    '<fieldname="turtle_foo"/>'+
                    '</tree>'+
                    '</field>'+
                    '</form>',
            });

            assert.strictEqual(form.$('td.o_data_cell').text(),"blipkawa",
                "shouldhaveloadeddefaultdata");

            form.destroy();
        });

        QUnit.test('many2manycheckboxeswithdefaultvalues',asyncfunction(assert){
            assert.expect(7);

            this.data.partner.fields.turtles.default=[3];
            this.data.partner.fields.turtles.type="many2many";

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<fieldname="turtles"widget="many2many_checkboxes">'+
                    '</field>'+
                    '</form>',
                mockRPC:function(route,args){
                    if(args.method==='create'){
                        assert.deepEqual(args.args[0].turtles,[[6,false,[1]]],
                            "correctvaluesshouldhavebeensenttocreate");
                    }
                    returnthis._super.apply(this,arguments);
                }
            });

            assert.notOk(form.$('.o_form_view.custom-checkboxinput').eq(0).prop('checked'),
                "firstcheckboxshouldnotbechecked");
            assert.notOk(form.$('.o_form_view.custom-checkboxinput').eq(1).prop('checked'),
                "secondcheckboxshouldnotbechecked");
            assert.ok(form.$('.o_form_view.custom-checkboxinput').eq(2).prop('checked'),
                "thirdcheckboxshouldbechecked");

            awaittestUtils.dom.click(form.$('.o_form_view.custom-checkboxinput:checked'));
            awaittestUtils.dom.click(form.$('.o_form_view.custom-checkboxinput').first());
            awaittestUtils.dom.click(form.$('.o_form_view.custom-checkboxinput').first());
            awaittestUtils.dom.click(form.$('.o_form_view.custom-checkboxinput').first());

            assert.ok(form.$('.o_form_view.custom-checkboxinput').eq(0).prop('checked'),
                "firstcheckboxshouldbechecked");
            assert.notOk(form.$('.o_form_view.custom-checkboxinput').eq(1).prop('checked'),
                "secondcheckboxshouldnotbechecked");
            assert.notOk(form.$('.o_form_view.custom-checkboxinput').eq(2).prop('checked'),
                "thirdcheckboxshouldnotbechecked");

            awaittestUtils.form.clickSave(form);

            form.destroy();
        });

        QUnit.test('many2manylistwithx2many:addarecord',asyncfunction(assert){
            assert.expect(18);

            this.data.partner_type.fields.m2m={
                string:"M2M",type:"many2many",relation:'turtle',
            };
            this.data.partner_type.records[0].m2m=[1,2];
            this.data.partner_type.records[1].m2m=[2,3];

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<fieldname="timmy"/>'+
                    '</form>',
                res_id:1,
                archs:{
                    'partner_type,false,list':'<tree>'+
                        '<fieldname="display_name"/>'+
                        '<fieldname="m2m"widget="many2many_tags"/>'+
                        '</tree>',
                    'partner_type,false,search':'<search>'+
                        '<fieldname="display_name"string="Name"/>'+
                        '</search>',
                },
                mockRPC:function(route,args){
                    if(args.method!=='load_views'){
                        assert.step(_.last(route.split('/'))+'on'+args.model);
                    }
                    if(args.model==='turtle'){
                        assert.step(JSON.stringify(args.args[0]));//thereadids
                    }
                    returnthis._super.apply(this,arguments);
                },
                viewOptions:{
                    mode:'edit',
                },
            });

            awaittestUtils.dom.click(form.$('.o_field_x2many_list_row_adda'));
            awaittestUtils.dom.click($('.modal.o_data_row:first'));

            assert.containsOnce(form,'.o_data_row',
                "therecordshouldhavebeenaddedtotherelation");
            assert.strictEqual(form.$('.o_data_row:first.o_badge_text').text(),'leonardodonatello',
                "innerm2mshouldhavebeenfetchedandcorrectlydisplayed");

            awaittestUtils.dom.click(form.$('.o_field_x2many_list_row_adda'));
            awaittestUtils.dom.click($('.modal.o_data_row:first'));

            assert.containsN(form,'.o_data_row',2,
                "thesecondrecordshouldhavebeenaddedtotherelation");
            assert.strictEqual(form.$('.o_data_row:nth(1).o_badge_text').text(),'donatelloraphael',
                "innerm2mshouldhavebeenfetchedandcorrectlydisplayed");

            assert.verifySteps([
                'readonpartner',
                'search_readonpartner_type',
                'readonturtle',
                '[1,2,3]',
                'readonpartner_type',
                'readonturtle',
                '[1,2]',
                'search_readonpartner_type',
                'readonturtle',
                '[2,3]',
                'readonpartner_type',
                'readonturtle',
                '[2,3]',
            ]);

            form.destroy();
        });

        QUnit.test('many2manywithadomain',asyncfunction(assert){
            //Thedomainspecifiedonthefieldshouldnotbereplacedbythepotential
            //domaintheuserwritesinthedialog,theyshouldratherbeconcatenated
            assert.expect(2);

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<fieldname="timmy"domain="[[\'display_name\',\'=\',\'gold\']]"/>'+
                    '</form>',
                res_id:1,
                archs:{
                    'partner_type,false,list':'<tree>'+
                        '<fieldname="display_name"/>'+
                        '</tree>',
                    'partner_type,false,search':'<search>'+
                        '<fieldname="display_name"string="Name"/>'+
                        '</search>',
                },
                viewOptions:{
                    mode:'edit',
                },
            });

            awaittestUtils.dom.click(form.$('.o_field_x2many_list_row_adda'));
            assert.strictEqual($('.modal.o_data_row').length,1,
                "shouldcontainonlyonerow(gold)");

            awaitcpHelpers.editSearch('.modal','s');
            awaitcpHelpers.validateSearch('.modal');

            assert.strictEqual($('.modal.o_data_row').length,0,"shouldcontainnorow");

            form.destroy();
        });

        QUnit.test('many2manylistwithonchangeandeditionofarecord',asyncfunction(assert){
            assert.expect(8);

            this.data.partner.fields.turtles.type="many2many";
            this.data.partner.onchanges.turtles=function(){};
            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<fieldname="turtles">'+
                    '<tree>'+
                    '<fieldname="turtle_foo"/>'+
                    '</tree>'+
                    '</field>'+
                    '</form>',
                res_id:1,
                archs:{
                    'turtle,false,form':'<formstring="TurtlePower"><fieldname="turtle_bar"/></form>',
                },
                mockRPC:function(route,args){
                    assert.step(args.method);
                    returnthis._super.apply(this,arguments);
                },
            });

            awaittestUtils.form.clickEdit(form);
            awaittestUtils.dom.click(form.$('td.o_data_cell:first'));

            awaittestUtils.dom.click($('.modal-bodyinput[type="checkbox"]'));
            awaittestUtils.dom.click($('.modal.modal-footer.btn-primary').first());

            //thereisnothinglefttosave->shouldnotdoa'write'RPC
            awaittestUtils.form.clickSave(form);

            assert.verifySteps([
                'read',//readinitialrecord(onpartner)
                'read',//readmany2manyturtles
                'load_views',//loadarchofturtlesformview
                'read',//readmissingfieldwhenopeningrecordinmodalformview
                'write',//whensavingthemodal
                'onchange',//onchangeshouldbetriggeredonpartner
                'read',//reloadmany2many
            ]);

            form.destroy();
        });

        QUnit.test('onchangewith40+commandsforamany2many',asyncfunction(assert){
            //thistestensuresthatthebasic_modelcorrectlyhandlesmoreLINK_TO
            //commandsthanthelimitofthedataPoint(40forx2manykanban)
            assert.expect(24);

            //createalotofpartner_typesthatwillbelinkedbytheonchange
            varcommands=[[5]];
            for(vari=0;i<45;i++){
                varid=100+i;
                this.data.partner_type.records.push({id:id,display_name:"type"+id});
                commands.push([4,id]);
            }
            this.data.partner.onchanges={
                foo:function(obj){
                    obj.timmy=commands;
                },
            };

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<fieldname="foo"/>'+
                    '<fieldname="timmy">'+
                    '<kanban>'+
                    '<fieldname="display_name"/>'+
                    '<templates>'+
                    '<tt-name="kanban-box">'+
                    '<div><tt-esc="record.display_name.value"/></div>'+
                    '</t>'+
                    '</templates>'+
                    '</kanban>'+
                    '</field>'+
                    '</form>',
                res_id:1,
                mockRPC:function(route,args){
                    assert.step(args.method);
                    if(args.method==='write'){
                        assert.strictEqual(args.args[1].timmy[0][0],6,
                            "shouldsendacommand6");
                        assert.strictEqual(args.args[1].timmy[0][2].length,45,
                            "shouldreplacewith45ids");
                    }
                    returnthis._super.apply(this,arguments);
                },
                viewOptions:{
                    mode:'edit',
                },
            });

            assert.verifySteps(['read']);

            awaittestUtils.fields.editInput(form.$('.o_field_widget[name=foo]'),'triggeronchange');

            assert.verifySteps(['onchange','read']);
            assert.strictEqual(form.$('.o_x2m_control_panel.o_pager_counter').text().trim(),
                '1-40/45',"pagershouldbecorrect");
            assert.strictEqual(form.$('.o_kanban_record:not(".o_kanban_ghost")').length,40,
                'thereshouldbe40recordsdisplayedonpage1');

            awaittestUtils.dom.click(form.$('.o_field_widget[name=timmy].o_pager_next'));
            assert.verifySteps(['read']);
            assert.strictEqual(form.$('.o_x2m_control_panel.o_pager_counter').text().trim(),
                '41-45/45',"pagershouldbecorrect");
            assert.strictEqual(form.$('.o_kanban_record:not(".o_kanban_ghost")').length,5,
                'thereshouldbe5recordsdisplayedonpage2');

            awaittestUtils.form.clickSave(form);

            assert.strictEqual(form.$('.o_x2m_control_panel.o_pager_counter').text().trim(),
                '1-40/45',"pagershouldbecorrect");
            assert.strictEqual(form.$('.o_kanban_record:not(".o_kanban_ghost")').length,40,
                'thereshouldbe40recordsdisplayedonpage1');

            awaittestUtils.dom.click(form.$('.o_field_widget[name=timmy].o_pager_next'));
            assert.strictEqual(form.$('.o_x2m_control_panel.o_pager_counter').text().trim(),
                '41-45/45',"pagershouldbecorrect");
            assert.strictEqual(form.$('.o_kanban_record:not(".o_kanban_ghost")').length,5,
                'thereshouldbe5recordsdisplayedonpage2');

            awaittestUtils.dom.click(form.$('.o_field_widget[name=timmy].o_pager_next'));
            assert.strictEqual(form.$('.o_x2m_control_panel.o_pager_counter').text().trim(),
                '1-40/45',"pagershouldbecorrect");
            assert.strictEqual(form.$('.o_kanban_record:not(".o_kanban_ghost")').length,40,
                'thereshouldbe40recordsdisplayedonpage1');

            assert.verifySteps(['write','read','read','read']);
            form.destroy();
        });

        QUnit.test('default_get,onchange,onchangeonm2m',asyncfunction(assert){
            assert.expect(1);

            this.data.partner.onchanges.int_field=function(obj){
                if(obj.int_field===2){
                    assert.deepEqual(obj.timmy,[
                        [6,false,[12]],
                        [1,12,{display_name:'gold'}]
                    ]);
                }
                obj.timmy=[
                    [5],
                    [1,12,{display_name:'gold'}]
                ];
            };

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<form>'+
                    '<sheet>'+
                    '<fieldname="timmy">'+
                    '<tree>'+
                    '<fieldname="display_name"/>'+
                    '</tree>'+
                    '</field>'+
                    '<fieldname="int_field"/>'+
                    '</sheet>'+
                    '</form>',
            });

            awaittestUtils.fields.editInput(form.$('.o_field_widget[name=int_field]'),2);
            form.destroy();
        });

        QUnit.test('widgetmany2many_tags',asyncfunction(assert){
            assert.expect(1);
            this.data.turtle.records[0].partner_ids=[2];

            varform=awaitcreateView({
                View:FormView,
                model:'turtle',
                data:this.data,
                arch:'<formstring="Turtles">'+
                    '<sheet>'+
                    '<fieldname="display_name"/>'+
                    '<fieldname="partner_ids"widget="many2many_tags"/>'+
                    '</sheet>'+
                    '</form>',
                res_id:1,
            });

            assert.deepEqual(
                form.$('.o_field_many2manytags.o_field_widget.badge.o_badge_text').attr('title'),
                'secondrecord','thetitleshouldbefilledin'
            );

            form.destroy();
        });

        QUnit.test('many2manytagswidget:selectmultiplerecords',asyncfunction(assert){
            assert.expect(5);
            for(vari=1;i<=10;i++){
                this.data.partner_type.records.push({id:100+i,display_name:"Partner"+i});
            }
            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<fieldname="display_name"/>'+
                    '<fieldname="timmy"widget="many2many_tags"/>'+
                    '</form>',
                res_id:1,
                archs:{
                    'partner_type,false,list':'<tree><fieldname="display_name"/></tree>',
                    'partner_type,false,search':'<search><fieldname="display_name"/></search>',
                },
            });
            awaittestUtils.form.clickEdit(form);
            awaittestUtils.fields.many2one.clickOpenDropdown('timmy');
            awaittestUtils.fields.many2one.clickItem('timmy','SearchMore');
            assert.ok($('.modal.o_list_view'),"shouldhaveopenthemodal");

            //+1fortheselectall
            assert.containsN($(document),'.modal.o_list_view.o_list_record_selectorinput',this.data.partner_type.records.length+1,
                "Shouldhaverecordselectorcheckboxestoselectmultiplerecords");
            //multipleselecttag
            awaittestUtils.dom.click($('.modal.o_list_viewthead.o_list_record_selectorinput'));
            assert.ok(!$('.modal.o_select_button').prop('disabled'),"selectbuttonshouldbeenabled");
            awaittestUtils.dom.click($('.o_select_button'));
            assert.containsNone($(document),'.modal.o_list_view',"shouldhaveclosedthemodal");
            assert.containsN(form,'.o_field_many2manytags[name="timmy"].badge',this.data.partner_type.records.length,
                "many2manytagshouldnowcontain12records");
            form.destroy();
        });

        QUnit.test("many2manytagswidget:selectmultiplerecordsdoesn'tshowalreadyaddedtags",asyncfunction(assert){
            assert.expect(5);
            for(vari=1;i<=10;i++){
                this.data.partner_type.records.push({id:100+i,display_name:"Partner"+i});
            }
            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<fieldname="display_name"/>'+
                    '<fieldname="timmy"widget="many2many_tags"/>'+
                    '</form>',
                res_id:1,
                archs:{
                    'partner_type,false,list':'<tree><fieldname="display_name"/></tree>',
                    'partner_type,false,search':'<search><fieldname="display_name"/></search>',
                },
            });
            awaittestUtils.form.clickEdit(form);


            awaittestUtils.fields.many2one.clickOpenDropdown('timmy');
            awaittestUtils.fields.many2one.clickItem('timmy','Partner1');

            awaittestUtils.fields.many2one.clickOpenDropdown('timmy');
            awaittestUtils.fields.many2one.clickItem('timmy','SearchMore');
            assert.ok($('.modal.o_list_view'),"shouldhaveopenthemodal");

            //-1fortheonethatisalreadyontheform&+1fortheselectall,
            assert.containsN($(document),'.modal.o_list_view.o_list_record_selectorinput',this.data.partner_type.records.length-1+1,
                "Shouldhaverecordselectorcheckboxestoselectmultiplerecords");
            //multipleselecttag
            awaittestUtils.dom.click($('.modal.o_list_viewthead.o_list_record_selectorinput'));
            assert.ok(!$('.modal.o_select_button').prop('disabled'),"selectbuttonshouldbeenabled");
            awaittestUtils.dom.click($('.o_select_button'));
            assert.containsNone($(document),'.modal.o_list_view',"shouldhaveclosedthemodal");
            assert.containsN(form,'.o_field_many2manytags[name="timmy"].badge',this.data.partner_type.records.length,
                "many2manytagshouldnowcontain12records");
            form.destroy();
        });

        QUnit.test("many2manytagswidget:save&newineditmodedoesn'tcloseeditwindow",asyncfunction(assert){
          assert.expect(5);
          for(vari=1;i<=10;i++){
              this.data.partner_type.records.push({id:100+i,display_name:"Partner"+i});
          }
          varform=awaitcreateView({
              View:FormView,
              model:'partner',
              data:this.data,
              arch:'<formstring="Partners">'+
                  '<fieldname="display_name"/>'+
                  '<fieldname="timmy"widget="many2many_tags"/>'+
                  '</form>',
              res_id:1,
              archs:{
                  'partner_type,false,list':'<tree><fieldname="display_name"/></tree>',
                  'partner_type,false,search':'<search><fieldname="display_name"/></search>',
                  'partner_type,false,form':'<form><fieldname="display_name"/></form>'
              },
          });
          awaittestUtils.form.clickEdit(form);

          awaittestUtils.fields.many2one.createAndEdit('timmy',"Ralts");
          assert.containsOnce($(document),'.modal.o_form_view',"shouldhaveopenedthemodal");

          //Createmultiplerecordswithsave&new
          awaittestUtils.fields.editInput($('.modalinput:first'),'Ralts');
          awaittestUtils.dom.click($('.modal.btn-primary:nth-child(2)'));
          assert.containsOnce($(document),'.modal.o_form_view',"modalshouldstillbeopen");
          assert.equal($('.modalinput:first')[0].value,'',"inputshouldbeempty")

          //Createanotherrecordandclicksave&close
          awaittestUtils.fields.editInput($('.modalinput:first'),'Pikachu');
          awaittestUtils.dom.click($('.modal.btn-primary:first'));
          assert.containsNone($(document),'.modal.o_list_view',"shouldhaveclosedthemodal");
          assert.containsN(form,'.o_field_many2manytags[name="timmy"].badge',2,"many2manytagshouldnowcontain2records");

          form.destroy();
        });

        QUnit.test("many2manytagswidget:maketagnameinputfieldblankonSave&New",asyncfunction(assert){
            assert.expect(4);

            letonchangeCalls=0;
            constform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<form><fieldname="timmy"widget="many2many_tags"/></form>',
                archs:{
                    'partner_type,false,form':'<form><fieldname="name"/></form>'
                },
                res_id:1,
                mockRPC:function(route,args){
                    if(args.method==='onchange'){
                        if(onchangeCalls===0){
                            assert.deepEqual(args.kwargs.context,{default_name:'hello'},
                                "contextshouldhavedefault_namewith'hello'asvalue");
                        }
                        if(onchangeCalls===1){
                            assert.deepEqual(args.kwargs.context,{},
                                "contextshouldhavedefault_namewithfalseasvalue");
                        }
                        onchangeCalls++;
                    }
                    returnthis._super.apply(this,arguments);
                },
            });

            awaittestUtils.form.clickEdit(form);

            awaittestUtils.fields.editInput($('.o_field_widgetinput'),'hello');
            awaittestUtils.fields.many2one.clickItem('timmy','CreateandEdit');
            assert.strictEqual(document.querySelector('.modal.o_form_viewinput').value,"hello",
                "shouldcontainthe'hello'inthetagnameinputfield");

            //Createrecordwithsave&new
            awaittestUtils.dom.click(document.querySelector('.modal.btn-primary:nth-child(2)'));
            assert.strictEqual(document.querySelector('.modal.o_form_viewinput').value,"",
                "shoulddisplaytheblankvalueinthetagnameinputfield");

            form.destroy();
        });

        QUnit.test('many2manylistadd*many*records,remove,re-add',asyncfunction(assert){
            assert.expect(5);

            this.data.partner.fields.timmy.domain=[['color','=',2]];
            this.data.partner.fields.timmy.onChange=true;
            this.data.partner_type.fields.product_ids={string:"Product",type:"many2many",relation:'product'};

            for(vari=0;i<50;i++){
                varnew_record_partner_type={id:100+i,display_name:"batch"+i,color:2};
                this.data.partner_type.records.push(new_record_partner_type);
            }

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<fieldname="timmy"widget="many2many">'+
                    '<tree>'+
                    '<fieldname="display_name"/>'+
                    '<fieldname="product_ids"widget="many2many_tags"/>'+
                    '</tree>'+
                    '</field>'+
                    '</form>',
                res_id:1,
                archs:{
                    'partner_type,false,list':'<tree><fieldname="display_name"/></tree>',
                    'partner_type,false,search':'<search><fieldname="display_name"/><fieldname="color"/></search>',
                },
                mockRPC:function(route,args){
                    if(args.method==='get_formview_id'){
                        assert.deepEqual(args.args[0],[1],"shouldcallget_formview_idwithcorrectid");
                        returnPromise.resolve(false);
                    }
                    returnthis._super(route,args);
                },
            });

            //Firstround:add51recordsinbatch
            awaittestUtils.dom.click(form.$buttons.find('.btn.btn-primary.o_form_button_edit'));
            awaittestUtils.dom.click(form.$('.o_field_x2many_list_row_adda'));

            var$modal=$('.modal-lg');

            assert.equal($modal.length,1,
                'Thereshouldbeonemodal');

            awaittestUtils.dom.click($modal.find('theadinput[type=checkbox]'));

            awaittestUtils.dom.click($modal.find('.btn.btn-primary.o_select_button'));

            assert.strictEqual(form.$('.o_data_row').length,51,
                'Weshouldhaveaddedalltherecordspresentinthesearchviewtothem2mfield');//the50inbatch+'gold'

            awaittestUtils.dom.click(form.$buttons.find('.btn.btn-primary.o_form_button_save'));

            //Secoundround:removeonerecord
            awaittestUtils.dom.click(form.$buttons.find('.btn.btn-primary.o_form_button_edit'));
            vartrash_buttons=form.$('.o_field_many2many.o_field_widget.o_field_x2many.o_field_x2many_list.o_list_record_remove');

            awaittestUtils.dom.click(trash_buttons.first());

            varpager_limit=form.$('.o_field_many2many.o_field_widget.o_field_x2many.o_field_x2many_list.o_pager_limit');
            assert.equal(pager_limit.text(),'50',
                'Weshouldhave50recordsinthem2mfield');

            //Thirdround:re-add1records
            awaittestUtils.dom.click(form.$('.o_field_x2many_list_row_adda'));

            $modal=$('.modal-lg');

            assert.equal($modal.length,1,
                'Thereshouldbeonemodal');

            awaittestUtils.dom.click($modal.find('theadinput[type=checkbox]'));

            awaittestUtils.dom.click($modal.find('.btn.btn-primary.o_select_button'));

            assert.strictEqual(form.$('.o_data_row').length,51,
                'Weshouldhave51recordsinthem2mfield');

            form.destroy();
        });

        QUnit.test('many2many_tagswidget:conditionalcreate/deleteactions',asyncfunction(assert){
            assert.expect(10);

            this.data.turtle.records[0].partner_ids=[2];
            for(vari=1;i<=10;i++){
                this.data.partner.records.push({id:100+i,display_name:"Partner"+i});
            }

            constform=awaitcreateView({
                View:FormView,
                model:'turtle',
                data:this.data,
                arch:`
                    <form>
                        <fieldname="display_name"/>
                        <fieldname="turtle_bar"/>
                        <fieldname="partner_ids"options="{'create':[('turtle_bar','=',True)],'delete':[('turtle_bar','=',True)]}"widget="many2many_tags"/>
                    </form>`,
                archs:{
                    'partner,false,list':'<tree><fieldname="name"/></tree>',
                    'partner,false,search':'<search/>',
                },
                res_id:1,
                viewOptions:{
                    mode:'edit',
                },
            });

            //turtle_baristrue->createanddeleteactionsareavailable
            assert.containsOnce(form,'.o_field_many2manytags.o_field_widget.badge.o_delete',
                'Xicononbadgesshouldnotbeavailable');

            awaittestUtils.fields.many2one.clickOpenDropdown('partner_ids');

            const$dropdown1=form.$('.o_field_many2oneinput').autocomplete('widget');
            assert.containsOnce($dropdown1,'li.o_m2o_start_typing:contains(Starttyping...)',
                'autocompleteshouldcontainStarttyping...');

            awaittestUtils.fields.many2one.clickItem('partner_ids','SearchMore');

            assert.containsN(document.body,'.modal.modal-footerbutton',3,
                'thereshouldbe3buttons(Select,CreateandCancel)availableinthemodalfooter');

            awaittestUtils.dom.click($('.modal.modal-footer.o_form_button_cancel'));

            //typesomethingthatdoesn'texist
            awaittestUtils.fields.editAndTrigger(form.$('.o_field_many2oneinput'),
                'Somethingthatdoesnotexist','keydown');
            //awaittestUtils.nextTick();
            assert.containsN(form.$('.o_field_many2oneinput').autocomplete('widget'),'li.o_m2o_dropdown_option',2,
                'autocompleteshouldcontainCreateandCreateandEdit...options');

            //setturtle_barfalse->createanddeleteactionsarenolongeravailable
            awaittestUtils.dom.click(form.$('.o_field_widget[name="turtle_bar"]input').first());

            //removeiconshouldstillbethereasitdoesn'tdeleterecordsbutratherremovelinks
            assert.containsOnce(form,'.o_field_many2manytags.o_field_widget.badge.o_delete',
                'Xicononbadgeshouldstillbethereevenafterturtle_barisnotchecked');

            awaittestUtils.fields.many2one.clickOpenDropdown('partner_ids');
            const$dropdown2=form.$('.o_field_many2oneinput').autocomplete('widget');

            //onlySearchMoreoptionshouldbeavailable
            assert.containsOnce($dropdown2,'li.o_m2o_dropdown_option',
                'autocompleteshouldcontainonlyoneoption');
            assert.containsOnce($dropdown2,'li.o_m2o_dropdown_option:contains(SearchMore)',
                'autocompleteoptionshouldbeSearchMore');

            awaittestUtils.fields.many2one.clickItem('partner_ids','SearchMore');

            assert.containsN(document.body,'.modal.modal-footerbutton',2,
                'thereshouldbe2buttons(SelectandCancel)availableinthemodalfooter');

            awaittestUtils.dom.click($('.modal.modal-footer.o_form_button_cancel'));

            //typesomethingthatdoesn'texist
            awaittestUtils.fields.editAndTrigger(form.$('.o_field_many2oneinput'),
                'Somethingthatdoesnotexist','keyup');
            //awaittestUtils.nextTick();

            //onlySearchMoreoptionshouldbeavailable
            assert.containsOnce($dropdown2,'li.o_m2o_dropdown_option',
                'autocompleteshouldcontainonlyoneoption');
            assert.containsOnce($dropdown2,'li.o_m2o_dropdown_option:contains(SearchMore)',
                'autocompleteoptionshouldbeSearchMore');

            form.destroy();
        });

        QUnit.test('failingmany2onequickcreateinamany2many_tags',asyncfunction(assert){
            assert.expect(5);

            varform=awaitcreateView({
                View:FormView,
                model:'partner',
                data:this.data,
                arch:'<form><fieldname="timmy"widget="many2many_tags"/></form>',
                mockRPC(route,args){
                    if(args.method==='name_create'){
                        returnPromise.reject();
                    }
                    if(args.method==='create'){
                        assert.deepEqual(args.args[0],{
                            color:8,
                            name:'newpartner',
                        });
                    }
                    returnthis._super.apply(this,arguments);
                },
                archs:{
                    'partner_type,false,form':`
                        <form>
                            <fieldname="name"/>
                            <fieldname="color"/>
                        </form>`,
                },
            });

            assert.containsNone(form,'.o_field_many2manytags.badge');

            //trytoquickcreatearecord
            awaittestUtils.dom.triggerEvent(form.$('.o_field_many2oneinput'),'focus');
            awaittestUtils.fields.many2one.searchAndClickItem('timmy',{
                search:'newpartner',
                item:'Create'
            });

            //asthequickcreatefailed,adialogshouldbeopento'slowcreate'therecord
            assert.containsOnce(document.body,'.modal.o_form_view');
            assert.strictEqual($('.modal.o_field_widget[name=name]').val(),'newpartner');

            awaittestUtils.fields.editInput($('.modal.o_field_widget[name=color]'),8);
            awaittestUtils.modal.clickButton('Save&Close');

            assert.containsOnce(form,'.o_field_many2manytags.badge');

            form.destroy();
        });
    });
});
});
