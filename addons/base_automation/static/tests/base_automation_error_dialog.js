flectra.define('base_automation.BaseAutomatioErrorDialogTests',function(require){
'usestrict';

    constCrashManager=require('web.CrashManager').CrashManager;
    constsession=require('web.session');

    QUnit.module('base_automation',{},function(){

        QUnit.module('ErrorDialog');

        QUnit.test('Errorduetoanautomatedaction',asyncfunction(assert){
            assert.expect(4);

            letbaseAutomationName='Testbaseautomationerrordialog';
            leterror={
                type:'FlectraClientError',
                message:'Message',
                data:{
                    debug:'Traceback',
                    context:{
                        exception_class:'base_automation',
                        base_automation:{
                            id:1,
                            name:baseAutomationName,
                        },
                    },
                },
            };
            //Forcetheusersessiontobeadmin,todisplaythedisableandeditactionbuttons,
            //thenresetbacktotheoriginvalueafterthetest.
            letisAdmin=session.is_admin;
            session.is_admin=true;

            letcrashManager=newCrashManager();
            letdialog=crashManager.show_error(error);

            awaitdialog._opened;

            assert.containsOnce(document.body,'.modal.o_clipboard_button');
            assert.containsOnce(document.body,'.modal.o_disable_action_button');
            assert.containsOnce(document.body,'.modal.o_edit_action_button');
            assert.ok(dialog.$el.text().indexOf(baseAutomationName)!==-1);

            session.is_admin=isAdmin;
            crashManager.destroy();
        });

        QUnit.test('Errornotduetoanautomatedaction',asyncfunction(assert){
            assert.expect(3);

            leterror={
                type:'FlectraClientError',
                message:'Message',
                data:{
                    debug:'Traceback',
                },
            };
            letcrashManager=newCrashManager();
            letdialog=crashManager.show_error(error);

            awaitdialog._opened;

            assert.containsOnce(document.body,'.modal.o_clipboard_button');
            assert.containsNone(document.body,'.modal.o_disable_action_button');
            assert.containsNone(document.body,'.modal.o_edit_action_button');

            crashManager.destroy();
        });

    });

});
