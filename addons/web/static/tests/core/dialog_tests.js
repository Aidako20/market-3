flectra.define('web.dialog_tests',function(require){
"usestrict";

varDialog=require('web.Dialog');
vartestUtils=require('web.test_utils');
varWidget=require('web.Widget');

varESCAPE_KEY=$.Event("keyup",{which:27});

asyncfunctioncreateEmptyParent(debug){
    varwidget=newWidget();

    awaittestUtils.mock.addMockEnvironment(widget,{
        debug:debug||false,
    });
    returnwidget;
}

QUnit.module('core',{},function(){

    QUnit.module('Dialog');

    QUnit.test("Closingcustomdialogusingbuttonscallsstandardcallback",asyncfunction(assert){
        assert.expect(3);

        vartestPromise=testUtils.makeTestPromiseWithAssert(assert,'customcallback');
        varparent=awaitcreateEmptyParent();
        newDialog(parent,{
            buttons:[
                {
                    text:"Close",
                    classes:'btn-primary',
                    close:true,
                    click:testPromise.resolve,
                },
            ],
            $content:$('<main/>'),
            onForceClose:testPromise.reject,
        }).open();

        assert.verifySteps([]);

        awaittestUtils.nextTick();
        awaittestUtils.dom.click($('.modal[role="dialog"].btn-primary'));

        testPromise.then(()=>{
            assert.verifySteps(['okcustomcallback']);
        });

        parent.destroy();
    });

    QUnit.test("Closingcustomdialogwithoutusingbuttonscallsforceclosecallback",asyncfunction(assert){
        assert.expect(3);

        vartestPromise=testUtils.makeTestPromiseWithAssert(assert,'customcallback');
        varparent=awaitcreateEmptyParent();
        newDialog(parent,{
            buttons:[
                {
                    text:"Close",
                    classes:'btn-primary',
                    close:true,
                    click:testPromise.reject,
                },
            ],
            $content:$('<main/>'),
            onForceClose:testPromise.resolve,
        }).open();

        assert.verifySteps([]);

        awaittestUtils.nextTick();
        awaittestUtils.dom.triggerEvents($('.modal[role="dialog"]'),[ESCAPE_KEY]);

        testPromise.then(()=>{
            assert.verifySteps(['okcustomcallback']);
        });

        parent.destroy();
    });

    QUnit.test("Closingconfirmdialogwithoutusingbuttonscallscancelcallback",asyncfunction(assert){
        assert.expect(3);

        vartestPromise=testUtils.makeTestPromiseWithAssert(assert,'confirmcallback');
        varparent=awaitcreateEmptyParent();
        varoptions={
            confirm_callback:testPromise.reject,
            cancel_callback:testPromise.resolve,
        };
        Dialog.confirm(parent,"",options);

        assert.verifySteps([]);

        awaittestUtils.nextTick();
        awaittestUtils.dom.triggerEvents($('.modal[role="dialog"]'),[ESCAPE_KEY]);

        testPromise.then(()=>{
            assert.verifySteps(['okconfirmcallback']);
        });

        parent.destroy();
    });

    QUnit.test("clicktwiceon'Ok'buttonofaconfirmdialog",asyncfunction(assert){
        assert.expect(5);

        vartestPromise=testUtils.makeTestPromise();
        varparent=awaitcreateEmptyParent();
        varoptions={
            confirm_callback:()=>{
                assert.step("confirm");
                returntestPromise;
            },
        };
        Dialog.confirm(parent,"",options);
        awaittestUtils.nextTick();

        assert.verifySteps([]);

        awaittestUtils.dom.click($('.modal[role="dialog"].btn-primary'));
        awaittestUtils.dom.click($('.modal[role="dialog"].btn-primary'));
        awaittestUtils.nextTick();
        assert.verifySteps(['confirm']);
        assert.ok($('.modal[role="dialog"]').hasClass('show'),"Shouldstillbeopened");
        testPromise.resolve();
        awaittestUtils.nextTick();
        assert.notOk($('.modal[role="dialog"]').hasClass('show'),"Shouldnowbeclosed");

        parent.destroy();
    });

    QUnit.test("clickon'Cancel'andthen'Ok'inaconfirmdialog",asyncfunction(assert){
        assert.expect(3);

        varparent=awaitcreateEmptyParent();
        varoptions={
            confirm_callback:()=>{
                thrownewError("shouldnotbecalled");
            },
            cancel_callback:()=>{
                assert.step("cancel");
            }
        };
        Dialog.confirm(parent,"",options);
        awaittestUtils.nextTick();

        assert.verifySteps([]);

        testUtils.dom.click($('.modal[role="dialog"]footerbutton:not(.btn-primary)'));
        testUtils.dom.click($('.modal[role="dialog"]footer.btn-primary'));
        assert.verifySteps(['cancel']);

        parent.destroy();
    });

    QUnit.test("clickon'Cancel'andthen'Ok'inaconfirmdialog(nocancelcallback)",asyncfunction(assert){
        assert.expect(2);

        varparent=awaitcreateEmptyParent();
        varoptions={
            confirm_callback:()=>{
                thrownewError("shouldnotbecalled");
            },
            //Cannotaddastepincancel_callback,that'sthepointofthis
            //test,we'llrelyoncheckingtheDialogisopenedthenclosed
            //withoutacrash.
        };
        Dialog.confirm(parent,"",options);
        awaittestUtils.nextTick();

        assert.ok($('.modal[role="dialog"]').hasClass('show'));
        testUtils.dom.click($('.modal[role="dialog"]footerbutton:not(.btn-primary)'));
        testUtils.dom.click($('.modal[role="dialog"]footer.btn-primary'));
        awaittestUtils.nextTick();
        assert.notOk($('.modal[role="dialog"]').hasClass('show'));

        parent.destroy();
    });

    QUnit.test("Confirmdialogcallbacksproperlyhandlerejections",asyncfunction(assert){
        assert.expect(5);

        varparent=awaitcreateEmptyParent();
        varoptions={
            confirm_callback:()=>{
                assert.step("confirm");
                returnPromise.reject();
            },
            cancel_callback:()=>{
                assert.step("cancel");
                return$.Deferred().reject();//Testjquerydeferredtoo
            }
        };
        Dialog.confirm(parent,"",options);
        awaittestUtils.nextTick();

        assert.verifySteps([]);
        testUtils.dom.click($('.modal[role="dialog"]footerbutton:not(.btn-primary)'));
        awaittestUtils.nextTick();
        testUtils.dom.click($('.modal[role="dialog"]footer.btn-primary'));
        awaittestUtils.nextTick();
        testUtils.dom.click($('.modal[role="dialog"]footerbutton:not(.btn-primary)'));
        assert.verifySteps(['cancel','confirm','cancel']);

        parent.destroy();
    });

    QUnit.test("Properlycanrelyonthethisinconfirmandcancelcallbacksofconfirmdialog",asyncfunction(assert){
        assert.expect(2);

        letdialogInstance=null;
        varparent=awaitcreateEmptyParent();
        varoptions={
            confirm_callback:function(){
                assert.equal(this,dialogInstance,"'this'isproperlyareferencetothedialoginstance");
                returnPromise.reject();
            },
            cancel_callback:function(){
                assert.equal(this,dialogInstance,"'this'isproperlyareferencetothedialoginstance");
                returnPromise.reject();
            }
        };
        dialogInstance=Dialog.confirm(parent,"",options);
        awaittestUtils.nextTick();

        testUtils.dom.click($('.modal[role="dialog"]footerbutton:not(.btn-primary)'));
        awaittestUtils.nextTick();
        testUtils.dom.click($('.modal[role="dialog"]footer.btn-primary'));

        parent.destroy();
    });

    QUnit.test("Confirmdialogcallbackscanreturnanythingwithoutcrash",asyncfunction(assert){
        assert.expect(3);
        //Notethatthistestcouldberemovedinmasteriftherelatedcode
        //isreworked.Thisonlypreventsastablefixtobreakthisagainby
        //relyingonthefactwhatisreturnedbythosecallbacksareundefined
        //orpromises.

        varparent=awaitcreateEmptyParent();
        varoptions={
            confirm_callback:()=>{
                assert.step("confirm");
                return5;
            },
        };
        Dialog.confirm(parent,"",options);
        awaittestUtils.nextTick();

        assert.verifySteps([]);
        testUtils.dom.click($('.modal[role="dialog"]footer.btn-primary'));
        assert.verifySteps(['confirm']);

        parent.destroy();
    });

    QUnit.test("Closingalertdialogwithoutusingbuttonscallsconfirmcallback",asyncfunction(assert){
        assert.expect(3);

        vartestPromise=testUtils.makeTestPromiseWithAssert(assert,'alertcallback');
        varparent=awaitcreateEmptyParent();
        varoptions={
            confirm_callback:testPromise.resolve,
        };
        Dialog.alert(parent,"",options);

        assert.verifySteps([]);

        awaittestUtils.nextTick();
        awaittestUtils.dom.triggerEvents($('.modal[role="dialog"]'),[ESCAPE_KEY]);

        testPromise.then(()=>{
            assert.verifySteps(['okalertcallback']);
        });

        parent.destroy();
    });

    QUnit.test("Ensureon_attach_callbackandon_detach_callbackareproperlycalled",asyncfunction(assert){
        assert.expect(4);

        constTestDialog=Dialog.extend({
            on_attach_callback(){
                assert.step('on_attach_callback');
            },
            on_detach_callback(){
                assert.step('on_detach_callback');
            },
        });

        constparent=awaitcreateEmptyParent();
        constdialog=newTestDialog(parent,{
            buttons:[
                {
                    text:"Close",
                    classes:'btn-primary',
                    close:true,
                },
            ],
            $content:$('<main/>'),
        }).open();

        awaitdialog.opened();

        assert.verifySteps(['on_attach_callback']);

        awaittestUtils.dom.click($('.modal[role="dialog"].btn-primary'));
        assert.verifySteps(['on_detach_callback']);

        parent.destroy();
    });

    QUnit.test("Shouldnotbedisplayedifparentisdestroyedwhiledialogisbeingopened",asyncfunction(assert){
        assert.expect(1);
        constparent=awaitcreateEmptyParent();
        constdialog=newDialog(parent);
        dialog.open();
        parent.destroy();
        awaittestUtils.nextTick();
        assert.containsNone(document.body,".modal[role='dialog']");
    });
});

});
