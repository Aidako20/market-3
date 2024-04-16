flectra.define('web.crash_manager_tests',function(require){
    "usestrict";
    constCrashManager=require('web.CrashManager').CrashManager;
    constBus=require('web.Bus');
    consttestUtils=require('web.test_utils');
    constcore=require('web.core');
    constcreateActionManager=testUtils.createActionManager;
    
QUnit.module('Services',{},function(){

    QUnit.module('CrashManager');

    QUnit.test("ExecuteanactionandclosetheRedirectWarningwhenclickingontheprimarybutton",asyncfunction(assert){
        assert.expect(4);

        vardummy_action_name="crash_manager_tests_dummy_action";
        vardummy_action=function(){
                assert.step('do_action');
            };
        core.action_registry.add(dummy_action_name,dummy_action);

        //Whatwewanttotestisado-actiontriggeredbythecrashManagerService
        //theinterceptfeatureoftestUtilsMockisnotfitforthis,becauseitistoolowinthehierarchy
        constbus=newBus();
        bus.on('do-action',null,payload=>{
            const{action,options}=payload;
            actionManager.doAction(action,options);
        });

        varactionManager=awaitcreateActionManager({
            actions:[dummy_action],
            services:{
                crash_manager:CrashManager,
            },
            bus
        });
        actionManager.call('crash_manager','rpc_error',{
            code:200,
            data:{
                name:"flectra.exceptions.RedirectWarning",
                arguments:[
                    "crash_manager_tests_warning_modal_text",
                    dummy_action_name,
                    "crash_manager_tests_button_text",
                    null,
                ]
            }
        });
        awaittestUtils.nextTick();

        varmodal_selector='div.modal:contains("crash_manager_tests_warning_modal_text")';
        assert.containsOnce($,modal_selector,"WarningModalshouldbeopened");

        awaittestUtils.dom.click($(modal_selector).find('button.btn-primary'));

        assert.containsNone($,modal_selector,"WarningModalshouldbeclosed");
        assert.verifySteps(['do_action'],"WarningModalPrimaryButtonActionshouldbeexecuted");
        
        actionManager.destroy();
    });
});
});
