flectra.define('mail.debugManagerTests',function(require){
"usestrict";

vartestUtils=require('web.test_utils');

varcreateDebugManager=testUtils.createDebugManager;

QUnit.module('MailDebugManager',{},function(){

    QUnit.test("ManageMessages",asyncfunction(assert){
        assert.expect(3);

        vardebugManager=awaitcreateDebugManager({
            intercepts:{
                do_action:function(event){
                    assert.deepEqual(event.data.action,{
                      context:{
                        default_res_model:"testModel",
                        default_res_id:5,
                      },
                        res_model:'mail.message',
                        name:"ManageMessages",
                        views:[[false,'list'],[false,'form']],
                        type:'ir.actions.act_window',
                        domain:[['res_id','=',5],['model','=','testModel']],
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
                    view_id:1,
                },
                type:"form",
            }],
        };
        varview={
            viewType:"form",
            getSelectedIds:function(){
                return[5];
            },
            modelName:'testModel',
        };
        awaittestUtils.nextTick();
        awaitdebugManager.update('action',action,view);

        var$messageMenu=debugManager.$('a[data-action=getMailMessages]');
        assert.strictEqual($messageMenu.length,1,"shouldhaveManageMessagemenuitem");
        assert.strictEqual($messageMenu.text().trim(),"ManageMessages",
            "shouldhavecorrectmenuitemtext");

        awaittestUtils.dom.click(debugManager.$('>a'));//opendropdown
        awaittestUtils.dom.click($messageMenu);

        debugManager.destroy();
    });
});
});
