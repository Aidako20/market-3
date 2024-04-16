flectra.define('web.debugManagerTests',function(require){
"usestrict";

vartestUtils=require('web.test_utils');
varFormView=require('web.FormView');

varcreateDebugManager=testUtils.createDebugManager;

QUnit.module('DebugManager',{},function(){

    QUnit.test("list:editviewmenuitem",asyncfunction(assert){
        assert.expect(3);

        vardebugManager=awaitcreateDebugManager();

        awaitdebugManager.appendTo($('#qunit-fixture'));

        //Simulateupdatedebugmanagerfromwebclient
        varaction={
            views:[{
                displayName:"List",
                fieldsView:{
                    view_id:1,
                },
                type:"list",
            }],
        };
        varview={
            viewType:"list",
        };
        awaittestUtils.nextTick();
        awaitdebugManager.update('action',action,view);

        var$editView=debugManager.$('a[data-action=edit][data-model="ir.ui.view"]');
        assert.strictEqual($editView.length,1,"shouldhaveeditviewmenuitem");
        assert.strictEqual($editView.text().trim(),"EditView:List",
            "shouldhavecorrectmenuitemtextforeditingview");
        assert.strictEqual($editView.data('id'),1,"shouldhavecorrectview_id");

        debugManager.destroy();
    });

    QUnit.test("form:ManageAttachmentsoption",asyncfunction(assert){
        assert.expect(3);

        vardebugManager=awaitcreateDebugManager({
            intercepts:{
                do_action:function(event){
                    assert.deepEqual(event.data.action,{
                      context:{
                        default_res_model:"test.model",
                        default_res_id:5,
                      },
                      domain:[["res_model","=","test.model"],["res_id","=",5]],
                      name:"ManageAttachments",
                      res_model:"ir.attachment",
                      type:"ir.actions.act_window",
                      views:[[false,"list"],[false,"form"]],
                    });
                },
            },
        });
        awaitdebugManager.appendTo($('#qunit-fixture'));

        //Simulateupdatedebugmanagerfromwebclient
        varaction={
            views:[{
                displayName:"Form",
                fieldsView:{
                    view_id:2,
                },
                type:"form",
            }],
            res_model:"test.model",
        };
        varview={
            viewType:"form",
            getSelectedIds:function(){
                return[5];
            },
        };
        awaitdebugManager.update('action',action,view);

        var$attachmentMenu=debugManager.$('a[data-action=get_attachments]');
        assert.strictEqual($attachmentMenu.length,1,"shouldhaveManageAttachmentsmenuitem");
        assert.strictEqual($attachmentMenu.text().trim(),"ManageAttachments",
            "shouldhavecorrectmenuitemtext");
        awaittestUtils.dom.click(debugManager.$('>a'));//opendropdown
        awaittestUtils.dom.click($attachmentMenu);

        debugManager.destroy();
    });

    QUnit.test("Debug:Setdefaultswithrightmodel",asyncfunction(assert){
        assert.expect(2);

        /* Clickondebug>setdefault,
         * setsomedefaults,clickonsave
         * modelandsomeotherdatashouldbesenttoserver
         */

        //We'llneedafullblownarchitecturewithsomedata
        vardata={
            partner:{
                fields:{
                    foo:{string:"Foo",type:"char",default:"MylittleFooValue"},
                },
                records:[{
                    id:1,
                    foo:"yop",
                }]
            },
            'ir.default':{//Wejustneedthistobedefined
                fields:{},
            },
        };

        varform=awaittestUtils.createView({
            View:FormView,
            model:'partner',
            data:data,
            arch:'<formstring="Partners">'+
                    '<fieldname="foo"/>'+
                '</form>',
            res_id:1,
        });

        //Nowtherealtestedcomponent
        vardebugManager=awaitcreateDebugManager({
            data:data,
            mockRPC:function(route,args){
                if(route=="/web/dataset/call_kw/ir.default/set"){
                    assert.deepEqual(args.args,["partner","foo","yop",true,true,false],
                        'Model,field,valueandbooleansforcurrentuser/companyshouldhavebeenpassed');
                    returnPromise.resolve();
                }
                returnthis._super.apply(this,arguments);
            }
        });

        awaitdebugManager.appendTo($('#qunit-fixture'));

        //Simulateupdatedebugmanagerfromwebclient
        varaction={
            controlPanelFieldsView:{},
            views:[{
                fieldsView:{
                    view_id:1,
                    model:'partner',
                    type:'form',
                },
                type:"form",
            }],
            res_model:'partner',
        };

        //Weareallset
        awaitdebugManager.update('action',action,form);

        //clickonset_defaultsdropdown
        awaittestUtils.dom.click(debugManager.$('>a'));//opendropdown
        awaittestUtils.dom.click(debugManager.$('a[data-action="set_defaults"]'));
        var$modal=$('.modal-content');
        assert.strictEqual($modal.length,1,'Onemodalpresent');

        $modal.find('select[id=formview_default_fields]option[value=foo]').prop('selected',true);

        //Save
        awaittestUtils.dom.click($modal.find('.modal-footerbutton').eq(1));

        form.destroy();
        debugManager.destroy();
    });
});
});
