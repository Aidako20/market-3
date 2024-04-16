flectra.define('barcodes.barcode_mobile_tests',function(){
    "usestrict";

    QUnit.module('Barcodes',{},function(){

        QUnit.module('BarcodesMobile');

        QUnit.test('barcodefieldautomaticallyfocusbehavior',function(assert){
            assert.expect(10);

            //MockChromemobileenvironment
            varbarcodeEvents=flectra.__DEBUG__.services["barcodes.BarcodeEvents"].BarcodeEvents;
            var__isChromeMobile=barcodeEvents.isChromeMobile;
            barcodeEvents.isChromeMobile=true;
            //Rebindkeyboardevents
            barcodeEvents.stop();
            barcodeEvents.start();

            var$form=$(
                '<form>'+
                    '<inputname="email"type="email"/>'+
                    '<inputname="number"type="number"/>'+
                    '<inputname="password"type="password"/>'+
                    '<inputname="tel"type="tel"/>'+
                    '<inputname="text"/>'+
                    '<inputname="explicit_text"type="text"/>'+
                    '<textarea></textarea>'+
                    '<divcontenteditable="true"></div>'+
                    '<selectname="select">'+
                        '<optionvalue="option1">Option1</option>'+
                        '<optionvalue="option2">Option2</option>'+
                    '</select>'+
                '</form>');
            $('#qunit-fixture').append($form);

            //Someelementsdoesn'tneedtokeepthefocus
            $('body').keydown();
            assert.strictEqual(document.activeElement.name,'barcode',
                "hiddenbarcodeinputshouldhavethefocus");

            var$element=$form.find('select');
            $element.focus().keydown();
            assert.strictEqual(document.activeElement.name,'barcode',
                "hiddenbarcodeinputshouldhavethefocus");

            //Thoseelementsabsolutelyneedtokeepthefocus:
            //inputselements:
            varkeepFocusedElements=['email','number','password','tel',
                'text','explicit_text'];
            for(vari=0;i<keepFocusedElements.length;++i){
                $element=$form.find('input[name='+keepFocusedElements[i]+']');
                $element.focus().keydown();
                assert.strictEqual(document.activeElement,$element[0],
                    "input"+keepFocusedElements[i]+"shouldkeepfocus");
            }
            //textareaelement
            $element=$form.find('textarea');
            $element.focus().keydown();
            assert.strictEqual(document.activeElement,$element[0],
                "textareashouldkeepfocus");
            //contenteditableelements
            $element=$form.find('[contenteditable=true]');
            $element.focus().keydown();
            assert.strictEqual(document.activeElement,$element[0],
                "contenteditableshouldkeepfocus");

            $('#qunit-fixture').empty();
            barcodeEvents.isChromeMobile=__isChromeMobile;
            //Rebindkeyboardevents
            barcodeEvents.stop();
            barcodeEvents.start();

            document.querySelector('input[name=barcode]').remove();
        });
    });
    });
