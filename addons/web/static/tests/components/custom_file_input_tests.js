flectra.define('web.custom_file_input_tests',function(require){
    "usestrict";

    constCustomFileInput=require('web.CustomFileInput');
    consttestUtils=require('web.test_utils');

    const{createComponent}=testUtils;

    QUnit.module('Components',{},function(){

        //Thismodulecannotbetestedasthoroughlyaswewantittobe:
        //browsersdonotletscriptsprogrammaticallyassignvaluestoinputs
        //oftypefile
        QUnit.module('CustomFileInput');

        QUnit.test("Uploadafile:defaultprops",asyncfunction(assert){
            assert.expect(6);

            constcustomFileInput=awaitcreateComponent(CustomFileInput,{
                env:{
                    services:{
                        asynchttpRequest(route,params){
                            assert.deepEqual(params,{
                                csrf_token:flectra.csrf_token,
                                ufile:[],
                            });
                            assert.step(route);
                            return'[]';
                        },
                    },
                },
            });
            constinput=customFileInput.el.querySelector('input');

            assert.strictEqual(customFileInput.el.innerText.trim().toUpperCase(),"CHOOSEFILE",
                "Fileinputtotaltextshouldmatchitsgiveninnerelement'stext");
            assert.strictEqual(input.accept,'*',
                "Inputshouldacceptallfilesbydefault");

            awaittestUtils.dom.triggerEvent(input,'change');

            assert.notOk(input.multiple,"'multiple'attributeshouldnotbeset");
            assert.verifySteps(['/web/binary/upload']);

            customFileInput.destroy();
        });

        QUnit.test("Uploadafile:customattachment",asyncfunction(assert){
            assert.expect(6);

            constcustomFileInput=awaitcreateComponent(CustomFileInput,{
                env:{
                    services:{
                        asynchttpRequest(route,params){
                            assert.deepEqual(params,{
                                id:5,
                                model:'res.model',
                                csrf_token:flectra.csrf_token,
                                ufile:[],
                            });
                            assert.step(route);
                            return'[]';
                        },
                    },
                },
                props:{
                    accepted_file_extensions:'.png',
                    action:'/web/binary/upload_attachment',
                    id:5,
                    model:'res.model',
                    multi_upload:true,
                },
                intercepts:{
                    'uploaded':ev=>assert.strictEqual(ev.detail.files.length,0,
                        "'files'propertyshouldbeanemptyarray"),
                },
            });
            constinput=customFileInput.el.querySelector('input');

            assert.strictEqual(input.accept,'.png',"Inputshouldnowonlyacceptpngs");

            awaittestUtils.dom.triggerEvent(input,'change');

            assert.ok(input.multiple,"'multiple'attributeshouldbeset");
            assert.verifySteps(['/web/binary/upload_attachment']);

            customFileInput.destroy();
        });
    });
});
