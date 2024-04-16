flectra.define('web.view_dialogs_tests',function(require){
"usestrict";

vardialogs=require('web.view_dialogs');
varListController=require('web.ListController');
vartestUtils=require('web.test_utils');
varWidget=require('web.Widget');
varFormView=require('web.FormView');

constcpHelpers=testUtils.controlPanel;
varcreateView=testUtils.createView;

asyncfunctioncreateParent(params){
    varwidget=newWidget();
    params.server=awaittestUtils.mock.addMockEnvironment(widget,params);
    returnwidget;
}

QUnit.module('Views',{
    beforeEach:function(){
        this.data={
            partner:{
                fields:{
                    display_name:{string:"Displayedname",type:"char"},
                    foo:{string:"Foo",type:'char'},
                    bar:{string:"Bar",type:"boolean"},
                    instrument:{string:'Instruments',type:'many2one',relation:'instrument'},
                },
                records:[
                    {id:1,foo:'blip',display_name:'blipblip',bar:true},
                    {id:2,foo:'tatatatata',display_name:'macgyver',bar:false},
                    {id:3,foo:'pioupiou',display_name:"JackO'Neill",bar:true},
                ],
            },
            instrument:{
                fields:{
                    name:{string:"name",type:"char"},
                    badassery:{string:'level',type:'many2many',relation:'badassery',domain:[['level','=','Awsome']]},
                },
            },

            badassery:{
                fields:{
                    level:{string:'level',type:"char"},
                },
                records:[
                    {id:1,level:'Awsome'},
                ],
            },

            product:{
                fields:{
                    name:{string:"name",type:"char"},
                    partner:{string:'Doors',type:'one2many',relation:'partner'},
                },
                records:[
                    {id:1,name:'Theend'},
                ],
            },
        };
    },
},function(){

    QUnit.module('view_dialogs');

    QUnit.test('formviewdialogbuttonsinfooterarepositionedproperly',asyncfunction(assert){
        assert.expect(2);

        varparent=awaitcreateParent({
            data:this.data,
            archs:{
                'partner,false,form':
                    '<formstring="Partner">'+
                        '<sheet>'+
                            '<group><fieldname="foo"/></group>'+
                            '<footer><buttonstring="CustomButton"type="object"class="btn-primary"/></footer>'+
                        '</sheet>'+
                    '</form>',
            },
        });

        newdialogs.FormViewDialog(parent,{
            res_model:'partner',
            res_id:1,
        }).open();
        awaittestUtils.nextTick();

        assert.notOk($('.modal-bodybutton').length,
            "shouldnothaveanybuttoninbody");
        assert.strictEqual($('.modal-footerbutton').length,1,
            "shouldhaveonlyonebuttoninfooter");
        parent.destroy();
    });

    QUnit.test('formviewdialogbuttonsinfooterarenotduplicated',asyncfunction(assert){
        assert.expect(2);
        this.data.partner.fields.poney_ids={string:"Poneys",type:"one2many",relation:'partner'};
        this.data.partner.records[0].poney_ids=[];

        varparent=awaitcreateParent({
            data:this.data,
            archs:{
                'partner,false,form':
                    '<formstring="Partner">'+
                            '<fieldname="poney_ids"><treeeditable="top"><fieldname="display_name"/></tree></field>'+
                            '<footer><buttonstring="CustomButton"type="object"class="btn-primary"/></footer>'+
                    '</form>',
            },
        });

        newdialogs.FormViewDialog(parent,{
            res_model:'partner',
            res_id:1,
        }).open();
        awaittestUtils.nextTick();

        assert.strictEqual($('.modalbutton.btn-primary').length,1,
            "shouldhave1buttonsinmodal");

        awaittestUtils.dom.click($('.o_field_x2many_list_row_adda'));
        awaittestUtils.fields.triggerKeydown($('input.o_input'),'escape');

        assert.strictEqual($('.modalbutton.btn-primary').length,1,
            "shouldstillhave1buttonsinmodal");
        parent.destroy();
    });

    QUnit.test('SelectCreateDialogusedomain,group_byandsearchdefault',asyncfunction(assert){
        assert.expect(3);

        varsearch=0;
        varparent=awaitcreateParent({
            data:this.data,
            archs:{
                'partner,false,list':
                    '<treestring="Partner">'+
                        '<fieldname="display_name"/>'+
                        '<fieldname="foo"/>'+
                    '</tree>',
                'partner,false,search':
                    '<search>'+
                        '<fieldname="foo"filter_domain="[(\'display_name\',\'ilike\',self),(\'foo\',\'ilike\',self)]"/>'+
                        '<groupexpand="0"string="GroupBy">'+
                            '<filtername="groupby_bar"context="{\'group_by\':\'bar\'}"/>'+
                        '</group>'+
                    '</search>',
            },
            mockRPC:function(route,args){
                if(args.method==='web_read_group'){
                    assert.deepEqual(args.kwargs,{
                        context:{
                            search_default_foo:"piou",
                            search_default_groupby_bar:true,
                        },
                        domain:["&",["display_name","like","a"],"&",["display_name","ilike","piou"],["foo","ilike","piou"]],
                        fields:["display_name","foo","bar"],
                        groupby:["bar"],
                        orderby:'',
                        lazy:true,
                        limit:80,
                    },"shouldsearchwiththecompletedomain(domain+search),andgroupby'bar'");
                }
                if(search===0&&route==='/web/dataset/search_read'){
                    search++;
                    assert.deepEqual(args,{
                        context:{
                            search_default_foo:"piou",
                            search_default_groupby_bar:true,
                            bin_size:true
                        }, //notpartofthetest,maychange
                        domain:["&",["display_name","like","a"],"&",["display_name","ilike","piou"],["foo","ilike","piou"]],
                        fields:["display_name","foo"],
                        model:"partner",
                        limit:80,
                        sort:""
                    },"shouldsearchwiththecompletedomain(domain+search)");
                }elseif(search===1&&route==='/web/dataset/search_read'){
                    assert.deepEqual(args,{
                        context:{
                            search_default_foo:"piou",
                            search_default_groupby_bar:true,
                            bin_size:true
                        }, //notpartofthetest,maychange
                        domain:[["display_name","like","a"]],
                        fields:["display_name","foo"],
                        model:"partner",
                        limit:80,
                        sort:""
                    },"shouldsearchwiththedomain");
                }

                returnthis._super.apply(this,arguments);
            },
        });

        vardialog;
        newdialogs.SelectCreateDialog(parent,{
            no_create:true,
            readonly:true,
            res_model:'partner',
            domain:[['display_name','like','a']],
            context:{
                search_default_groupby_bar:true,
                search_default_foo:'piou',
            },
        }).open().then(function(result){
            dialog=result;
        });
        awaittestUtils.nextTick();
        awaitcpHelpers.removeFacet('.modal',"Bar");
        awaitcpHelpers.removeFacet('.modal');

        parent.destroy();
    });

    QUnit.test('SelectCreateDialogcorrectlyevaluatesdomains',asyncfunction(assert){
        assert.expect(1);

        varparent=awaitcreateParent({
            data:this.data,
            archs:{
                'partner,false,list':
                    '<treestring="Partner">'+
                        '<fieldname="display_name"/>'+
                        '<fieldname="foo"/>'+
                    '</tree>',
                'partner,false,search':
                    '<search>'+
                        '<fieldname="foo"/>'+
                    '</search>',
            },
            mockRPC:function(route,args){
                if(route==='/web/dataset/search_read'){
                    assert.deepEqual(args.domain,[['id','=',2]],
                        "shouldhavecorrectlyevaluatedthedomain");
                }
                returnthis._super.apply(this,arguments);
            },
            session:{
                user_context:{uid:2},
            },
        });

        newdialogs.SelectCreateDialog(parent,{
            no_create:true,
            readonly:true,
            res_model:'partner',
            domain:"[['id','=',uid]]",
        }).open();
        awaittestUtils.nextTick();

        parent.destroy();
    });

    QUnit.test('SelectCreateDialoglistviewinreadonly',asyncfunction(assert){
        assert.expect(1);

        varparent=awaitcreateParent({
            data:this.data,
            archs:{
                'partner,false,list':
                    '<treestring="Partner"editable="bottom">'+
                        '<fieldname="display_name"/>'+
                        '<fieldname="foo"/>'+
                    '</tree>',
                'partner,false,search':
                    '<search/>'
            },
        });

        vardialog;
        newdialogs.SelectCreateDialog(parent,{
            res_model:'partner',
        }).open().then(function(result){
            dialog=result;
        });
        awaittestUtils.nextTick();

        //clickonthefirstrowtoseeifthelistiseditable
        awaittestUtils.dom.click(dialog.$('.o_list_viewtbodytr:firsttd:not(.o_list_record_selector):first'));

        assert.equal(dialog.$('.o_list_viewtbodytr:firsttd:not(.o_list_record_selector):firstinput').length,0,
            "listviewshouldnotbeeditableinaSelectCreateDialog");

        parent.destroy();
    });

    QUnit.test('SelectCreateDialogcascadex2manyincreatemode',asyncfunction(assert){
        assert.expect(5);

        varform=awaitcreateView({
            View:FormView,
            model:'product',
            data:this.data,
            arch:'<form>'+
                     '<fieldname="name"/>'+
                     '<fieldname="partner"widget="one2many">'+
                        '<treeeditable="top">'+
                            '<fieldname="display_name"/>'+
                            '<fieldname="instrument"/>'+
                        '</tree>'+
                    '</field>'+
                  '</form>',
            res_id:1,
            archs:{
                'partner,false,form':'<form>'+
                                           '<fieldname="name"/>'+
                                           '<fieldname="instrument"widget="one2many"mode="tree"/>'+
                                        '</form>',

                'instrument,false,form':'<form>'+
                                            '<fieldname="name"/>'+
                                            '<fieldname="badassery">'+
                                                '<tree>'+
                                                    '<fieldname="level"/>'+
                                                '</tree>'+
                                            '</field>'+
                                        '</form>',

                'badassery,false,list':'<tree>'+
                                                '<fieldname="level"/>'+
                                            '</tree>',

                'badassery,false,search':'<search>'+
                                                '<fieldname="level"/>'+
                                            '</search>',
            },

            mockRPC:function(route,args){
                if(route==='/web/dataset/call_kw/partner/get_formview_id'){
                    returnPromise.resolve(false);
                }
                if(route==='/web/dataset/call_kw/instrument/get_formview_id'){
                    returnPromise.resolve(false);
                }
                if(route==='/web/dataset/call_kw/instrument/create'){
                    assert.deepEqual(args.args,[{badassery:[[6,false,[1]]],name:"ABC"}],
                        'Themethodcreateshouldhavebeencalledwiththerightarguments');
                    returnPromise.resolve(false);
                }
                returnthis._super(route,args);
            },
        });

        awaittestUtils.form.clickEdit(form);
        awaittestUtils.dom.click(form.$('.o_field_x2many_list_row_adda'));
        awaittestUtils.fields.many2one.createAndEdit("instrument");

        var$modal=$('.modal-lg');

        assert.equal($modal.length,1,
            'Thereshouldbeonemodal');

        awaittestUtils.dom.click($modal.find('.o_field_x2many_list_row_adda'));

        var$modals=$('.modal-lg');

        assert.equal($modals.length,2,
            'Thereshouldbetwomodals');

        var$second_modal=$modals.not($modal);
        awaittestUtils.dom.click($second_modal.find('.o_list_table.table.table-sm.table-striped.o_list_table_ungrouped.o_data_rowinput[type=checkbox]'));

        awaittestUtils.dom.click($second_modal.find('.o_select_button'));

        $modal=$('.modal-lg');

        assert.equal($modal.length,1,
            'Thereshouldbeonemodal');

        assert.equal($modal.find('.o_data_cell').text(),'Awsome',
            'Thereshouldbeoneiteminthelistofthemodal');

        awaittestUtils.dom.click($modal.find('.btn.btn-primary'));

        form.destroy();
    });

    QUnit.test('Formdialogandsubviewwith_view_refcontexts',asyncfunction(assert){
        assert.expect(2);

        this.data.instrument.records=[{id:1,name:'Tromblon',badassery:[1]}];
        this.data.partner.records[0].instrument=1;

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<form>'+
                     '<fieldname="name"/>'+
                     '<fieldname="instrument"context="{\'tree_view_ref\':\'some_tree_view\'}"/>'+
                  '</form>',
            res_id:1,
            archs:{
                'instrument,false,form':'<form>'+
                                            '<fieldname="name"/>'+
                                            '<fieldname="badassery"context="{\'tree_view_ref\':\'some_other_tree_view\'}"/>'+
                                        '</form>',

                'badassery,false,list':'<tree>'+
                                                '<fieldname="level"/>'+
                                            '</tree>',
            },
            viewOptions:{
                mode:'edit',
            },

            mockRPC:function(route,args){
                if(args.method==='get_formview_id'){
                    returnPromise.resolve(false);
                }
                returnthis._super(route,args);
            },

            interceptsPropagate:{
                load_views:function(ev){
                    varevaluatedContext=ev.data.context;
                    if(ev.data.modelName==='instrument'){
                        assert.deepEqual(evaluatedContext,{tree_view_ref:'some_tree_view'},
                            'Thecorrect_view_refshouldhavebeensenttotheserver,firsttime');
                    }
                    if(ev.data.modelName==='badassery'){
                        assert.deepEqual(evaluatedContext,{
                            base_model_name:'instrument',
                            tree_view_ref:'some_other_tree_view',
                        },'Thecorrect_view_refshouldhavebeensenttotheserverforthesubview');
                    }
                },
            },
        });

        awaittestUtils.dom.click(form.$('.o_field_widget[name="instrument"]button.o_external_button'));
        form.destroy();
    });

    QUnit.test("Formdialogreplacesthecontextwith_createContextmethodwhenspecified",asyncfunction(assert){
        assert.expect(5);

        constparent=awaitcreateParent({
            data:this.data,
            archs:{
                "partner,false,form":
                    `<formstring="Partner">
                        <sheet>
                            <group><fieldname="foo"/></group>
                        </sheet>
                    </form>`,
            },

            mockRPC:function(route,args){
                if(args.method==="create"){
                    assert.step(JSON.stringify(args.kwargs.context));
                }
                returnthis._super(route,args);
            },
        });

        newdialogs.FormViewDialog(parent,{
            res_model:"partner",
            context:{answer:42},
            _createContext:()=>({dolphin:64}),
        }).open();
        awaittestUtils.nextTick();

        assert.notOk($(".modal-bodybutton").length,
            "shouldnothaveanybuttoninbody");
        assert.strictEqual($(".modal-footerbutton").length,3,
            "shouldhave3buttonsinfooter");

        awaittestUtils.dom.click($(".modal-footerbutton:contains(Save&New)"));
        awaittestUtils.dom.click($(".modal-footerbutton:contains(Save&New)"));
        assert.verifySteps(['{"answer":42}','{"dolphin":64}']);
        parent.destroy();
    });

    QUnit.test("Formdialogkeepsfullcontextwhenno_createContextisspecified",asyncfunction(assert){
        assert.expect(5);

        constparent=awaitcreateParent({
            data:this.data,
            archs:{
                "partner,false,form":
                    `<formstring="Partner">
                        <sheet>
                            <group><fieldname="foo"/></group>
                        </sheet>
                    </form>`,
            },

            mockRPC:function(route,args){
                if(args.method==="create"){
                    assert.step(JSON.stringify(args.kwargs.context));
                }
                returnthis._super(route,args);
            },
        });

        newdialogs.FormViewDialog(parent,{
            res_model:"partner",
            context:{answer:42}
        }).open();
        awaittestUtils.nextTick();

        assert.notOk($(".modal-bodybutton").length,
            "shouldnothaveanybuttoninbody");
        assert.strictEqual($(".modal-footerbutton").length,3,
            "shouldhave3buttonsinfooter");

        awaittestUtils.dom.click($(".modal-footerbutton:contains(Save&New)"));
        awaittestUtils.dom.click($(".modal-footerbutton:contains(Save&New)"));
        assert.verifySteps(['{"answer":42}','{"answer":42}']);
        parent.destroy();
    });

    QUnit.test('SelectCreateDialog:savecurrentsearch',asyncfunction(assert){
        assert.expect(4);

        testUtils.mock.patch(ListController,{
            getOwnedQueryParams:function(){
                return{
                    context:{
                        shouldBeInFilterContext:true,
                    },
                };
            },
        });

        varparent=awaitcreateParent({
            data:this.data,
            archs:{
                'partner,false,list':
                    '<tree>'+
                        '<fieldname="display_name"/>'+
                    '</tree>',
                'partner,false,search':
                    '<search>'+
                       '<filtername="bar"help="Bar"domain="[(\'bar\',\'=\',True)]"/>'+
                    '</search>',

            },
            env:{
                dataManager:{
                    create_filter:function(filter){
                        assert.strictEqual(filter.domain,`[("bar","=",True)]`,
                            "shouldsavethecorrectdomain");
                        constexpectedContext={
                            group_by:[],//defaultgroupbyisanemptylist
                            shouldBeInFilterContext:true,
                        };
                        assert.deepEqual(filter.context,expectedContext,
                            "shouldsavethecorrectcontext");
                    },
                }
            },
        });

        vardialog;
        newdialogs.SelectCreateDialog(parent,{
            context:{shouldNotBeInFilterContext:false},
            res_model:'partner',
        }).open().then(function(result){
            dialog=result;
        });
        awaittestUtils.nextTick();


        assert.containsN(dialog,'.o_data_row',3,"shouldcontain3records");

        //filteronbar
        awaitcpHelpers.toggleFilterMenu('.modal');
        awaitcpHelpers.toggleMenuItem('.modal',"Bar");

        assert.containsN(dialog,'.o_data_row',2,"shouldcontain2records");

        //savefilter
        awaitcpHelpers.toggleFavoriteMenu('.modal');
        awaitcpHelpers.toggleSaveFavorite('.modal');
        awaitcpHelpers.editFavoriteName('.modal',"somename");
        awaitcpHelpers.saveFavorite('.modal');

        testUtils.mock.unpatch(ListController);
        parent.destroy();
    });

    QUnit.test('SelectCreateDialogcallson_selectedwitheveryrecordmatchingthedomain',asyncfunction(assert){
        assert.expect(3);

        constparent=awaitcreateParent({
            data:this.data,
            archs:{
                'partner,false,list':
                    '<treelimit="2"string="Partner">'+
                        '<fieldname="display_name"/>'+
                        '<fieldname="foo"/>'+
                    '</tree>',
                'partner,false,search':
                    '<search>'+
                        '<fieldname="foo"/>'+
                    '</search>',
            },
            session:{},
        });

        newdialogs.SelectCreateDialog(parent,{
            res_model:'partner',
            on_selected:function(records){
                assert.equal(records.length,3);
                assert.strictEqual(records.map((r)=>r.display_name).toString(),"blipblip,macgyver,JackO'Neill");
                assert.strictEqual(records.map((r)=>r.id).toString(),"1,2,3");
            }
        }).open();
        awaittestUtils.nextTick();

        awaittestUtils.dom.click($('thead.o_list_record_selectorinput'));
        awaittestUtils.dom.click($('.o_list_selection_box.o_list_select_domain'));
        awaittestUtils.dom.click($('.modal.o_select_button'));

        parent.destroy();
    });

    QUnit.test('SelectCreateDialogcallson_selectedwitheveryrecordmatchingwithoutselectingadomain',asyncfunction(assert){
        assert.expect(3);

        constparent=awaitcreateParent({
            data:this.data,
            archs:{
                'partner,false,list':
                    '<treelimit="2"string="Partner">'+
                        '<fieldname="display_name"/>'+
                        '<fieldname="foo"/>'+
                    '</tree>',
                'partner,false,search':
                    '<search>'+
                        '<fieldname="foo"/>'+
                    '</search>',
            },
            session:{},
        });

        newdialogs.SelectCreateDialog(parent,{
            res_model:'partner',
            on_selected:function(records){
                assert.equal(records.length,2);
                assert.strictEqual(records.map((r)=>r.display_name).toString(),"blipblip,macgyver");
                assert.strictEqual(records.map((r)=>r.id).toString(),"1,2");
            }
        }).open();
        awaittestUtils.nextTick();

        awaittestUtils.dom.click($('thead.o_list_record_selectorinput'));
        awaittestUtils.dom.click($('.o_list_selection_box'));
        awaittestUtils.dom.click($('.modal.o_select_button'));

        parent.destroy();
    });

    QUnit.test('propagatecan_createontothesearchpopupo2m',asyncfunction(assert){
        assert.expect(4);

        this.data.instrument.records=[
            {id:1,name:'Tromblon1'},
            {id:2,name:'Tromblon2'},
            {id:3,name:'Tromblon3'},
            {id:4,name:'Tromblon4'},
            {id:5,name:'Tromblon5'},
            {id:6,name:'Tromblon6'},
            {id:7,name:'Tromblon7'},
            {id:8,name:'Tromblon8'},
        ];

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<form>'+
                     '<fieldname="name"/>'+
                     '<fieldname="instrument"can_create="false"/>'+
                  '</form>',
            res_id:1,
            archs:{
                'instrument,false,list':'<tree>'+
                                                '<fieldname="name"/>'+
                                            '</tree>',
                'instrument,false,search':'<search>'+
                                                '<fieldname="name"/>'+
                                            '</search>',
            },
            viewOptions:{
                mode:'edit',
            },

            mockRPC:function(route,args){
                if(args.method==='get_formview_id'){
                    returnPromise.resolve(false);
                }
                returnthis._super(route,args);
            },
        });

        awaittestUtils.fields.many2one.clickOpenDropdown('instrument');

        assert.containsNone(form,'.ui-autocompletea:contains(Starttyping...)');

        awaittestUtils.fields.editInput(form.el.querySelector(".o_field_many2one[name=instrument]input"),"a");

        assert.containsNone(form,'.ui-autocompletea:contains(CreateandEdit)');

        awaittestUtils.fields.editInput(form.el.querySelector(".o_field_many2one[name=instrument]input"),"");
        awaittestUtils.fields.many2one.clickItem('instrument','SearchMore...');

        var$modal=$('.modal-dialog.modal-lg');

        assert.strictEqual($modal.length,1,'Modalpresent');

        assert.strictEqual($modal.find('.modal-footerbutton').text(),"Cancel",
            'Onlythecancelbuttonispresentinmodal');

        form.destroy();
    });

    QUnit.test('formviewdialogisnotclosedwhenbuttonhandlersreturnarejectedpromise',asyncfunction(assert){
        assert.expect(3);

        this.data.partner.fields.poney_ids={string:"Poneys",type:"one2many",relation:'partner'};
        this.data.partner.records[0].poney_ids=[];
        varreject=true;

        varparent=awaitcreateParent({
            data:this.data,
            archs:{
                'partner,false,form':
                    '<formstring="Partner">'+
                    '<fieldname="poney_ids"><tree><fieldname="display_name"/></tree></field>'+
                    '</form>',
            },
        });

        newdialogs.FormViewDialog(parent,{
            res_model:'partner',
            res_id:1,
            buttons:[{
                text:'Clickme!',
                classes:"btn-secondaryo_form_button_magic",
                close:true,
                click:function(){
                    returnreject?Promise.reject():Promise.resolve();
                },
            }],
        }).open();

        awaittestUtils.nextTick();
        assert.strictEqual($('.modal').length,1,"shouldhaveamodaldisplayed");

        awaittestUtils.dom.click($('.modal.o_form_button_magic'));
        assert.strictEqual($('.modal').length,1,"modalshouldstillbeopened");

        reject=false;
        awaittestUtils.dom.click($('.modal.o_form_button_magic'));
        assert.strictEqual($('.modal').length,0,"modalshouldbeclosed");

        parent.destroy();
    });

});

});
