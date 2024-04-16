flectra.define('web.datepicker_tests',function(require){
    "usestrict";

    const{DatePicker,DateTimePicker}=require('web.DatePickerOwl');
    consttestUtils=require('web.test_utils');
    consttime=require('web.time');
    constCustomFilterItem=require('web.CustomFilterItem');
    constActionModel=require('web/static/src/js/views/action_model.js');

    const{createComponent}=testUtils;

    QUnit.module('Components',{},function(){

        QUnit.module('DatePicker');

        QUnit.test("basicrendering",asyncfunction(assert){
            assert.expect(8);

            constpicker=awaitcreateComponent(DatePicker,{
                props:{date:moment('01/09/1997')},
            });

            assert.containsOnce(picker,'input.o_input.o_datepicker_input');
            assert.containsOnce(picker,'span.o_datepicker_button');
            assert.containsNone(document.body,'div.bootstrap-datetimepicker-widget');

            constinput=picker.el.querySelector('input.o_input.o_datepicker_input');
            assert.strictEqual(input.value,'01/09/1997',
                "Valueshouldbetheonegiven")
                ;
            assert.strictEqual(input.dataset.target,`#${picker.el.id}`,
                "DatePickeridshouldmatchitsinputtarget");

            awaittestUtils.dom.click(input);

            assert.containsOnce(document.body,'div.bootstrap-datetimepicker-widget.datepicker');
            assert.containsNone(document.body,'div.bootstrap-datetimepicker-widget.timepicker');
            assert.strictEqual(
                document.querySelector('.datepicker.day.active').dataset.day,
                '01/09/1997',
                "Datepickershouldhavesetthecorrectday"
            );

            picker.destroy();
        });

        QUnit.test("pickadate",asyncfunction(assert){
            assert.expect(5);

            constpicker=awaitcreateComponent(DatePicker,{
                props:{date:moment('01/09/1997')},
                intercepts:{
                    'datetime-changed':ev=>{
                        assert.step('datetime-changed');
                        assert.strictEqual(ev.detail.date.format('MM/DD/YYYY'),'02/08/1997',
                            "Eventshouldtransmitthecorrectdate");
                    },
                }
            });
            constinput=picker.el.querySelector('.o_datepicker_input');

            awaittestUtils.dom.click(input);
            awaittestUtils.dom.click(document.querySelector('.datepickerth.next'));//nextmonth

            assert.verifySteps([]);

            awaittestUtils.dom.click(document.querySelectorAll('.datepickertabletd')[15]);//previousday

            assert.strictEqual(input.value,'02/08/1997');
            assert.verifySteps(['datetime-changed']);

            picker.destroy();
        });

        QUnit.test("pickadatewithlocale",asyncfunction(assert){
            assert.expect(4);

            //weirdshitofmomenthttps://github.com/moment/moment/issues/5600
            //Whenmonthregexreturnsundefined,januaryistaken(firstmonthofthedefault"nameless"locale)
            constoriginalLocale=moment.locale();
            //ThoseparameterswillmakeMoment'sinternalcomputestuffthatarerelevanttothebug
            constmonths='janvier_février_mars_avril_mai_juin_juillet_août_septembre_octobre_novembre_décembre'.split('_');
            constmonthsShort='janv._févr._mars_avr._mai_juin_juil._août_custSept._oct._nov._déc.'.split('_');
            moment.defineLocale('frenchForTests',{months,monthsShort,code:'frTest',monthsParseExact:true});

            consthasChanged=testUtils.makeTestPromise();
            constpicker=awaitcreateComponent(DatePicker,{
                translateParameters:{
                    date_format:"%d%b,%Y",//Thoseareimportanttoo
                    time_format:"%H:%M:%S",
                },
                props:{date:moment('09/01/1997','MM/DD/YYYY')},
                intercepts:{
                    'datetime-changed':ev=>{
                        assert.step('datetime-changed');
                        assert.strictEqual(ev.detail.date.format('MM/DD/YYYY'),'09/02/1997',
                            "Eventshouldtransmitthecorrectdate");
                        hasChanged.resolve();
                    },
                }
            });
            constinput=picker.el.querySelector('.o_datepicker_input');
            awaittestUtils.dom.click(input);

            awaittestUtils.dom.click(document.querySelectorAll('.datepickertabletd')[3]);//nextday

            assert.strictEqual(input.value,'02custSept.,1997');
            assert.verifySteps(['datetime-changed']);

            moment.locale(originalLocale);
            moment.updateLocale('englishForTest',null);

            picker.destroy();
        });

        QUnit.test("enteradatevalue",asyncfunction(assert){
            assert.expect(5);

            constpicker=awaitcreateComponent(DatePicker,{
                props:{date:moment('01/09/1997')},
                intercepts:{
                    'datetime-changed':ev=>{
                        assert.step('datetime-changed');
                        assert.strictEqual(ev.detail.date.format('MM/DD/YYYY'),'02/08/1997',
                            "Eventshouldtransmitthecorrectdate");
                    },
                }
            });
            constinput=picker.el.querySelector('.o_datepicker_input');

            assert.verifySteps([]);

            awaittestUtils.fields.editAndTrigger(input,'02/08/1997',['change']);

            assert.verifySteps(['datetime-changed']);

            awaittestUtils.dom.click(input);

            assert.strictEqual(
                document.querySelector('.datepicker.day.active').dataset.day,
                '02/08/1997',
                "Datepickershouldhavesetthecorrectday"
            );

            picker.destroy();
        });

        QUnit.test("Dateformatiscorrectlyset",asyncfunction(assert){
            assert.expect(2);

            testUtils.patch(time,{getLangDateFormat:()=>"YYYY/MM/DD"});
            constpicker=awaitcreateComponent(DatePicker,{
                props:{date:moment('01/09/1997')},
            });
            constinput=picker.el.querySelector('.o_datepicker_input');

            assert.strictEqual(input.value,'1997/01/09');

            //Forcesanupdatetoassertthattheregisteredformatisthecorrectone
            awaittestUtils.dom.click(input);

            assert.strictEqual(input.value,'1997/01/09');

            picker.destroy();
            testUtils.unpatch(time);
        });

        QUnit.test('customfilterdate',asyncfunction(assert){
            assert.expect(5);

            classMockedSearchModelextendsActionModel{
                dispatch(method,...args){
                    assert.strictEqual(method,'createNewFilters');
                    constpreFilters=args[0];
                    constpreFilter=preFilters[0];
                    assert.strictEqual(preFilter.description,
                        'Adateisequalto"05/05/2005"',
                        "descriptionshouldbeinlocalizedformat");
                    assert.deepEqual(preFilter.domain,
                        '[["date_field","=","2005-05-05"]]',
                        "domainshouldbeinUTCformat");
                }
            }
            constsearchModel=newMockedSearchModel();
            constdate_field={name:'date_field',string:"Adate",type:'date',searchable:true};
            constcfi=awaitcreateComponent(CustomFilterItem,{
                props:{
                    fields:{date_field},
                },
                env:{searchModel},
            });

            awaittestUtils.controlPanel.toggleAddCustomFilter(cfi);
            awaittestUtils.fields.editSelect(cfi.el.querySelector('.o_generator_menu_field'),'date_field');
            constvalueInput=cfi.el.querySelector('.o_generator_menu_value.o_input');
            awaittestUtils.dom.click(valueInput);
            assert.containsOnce(document.body,'.datepicker');
            awaittestUtils.fields.editSelect(valueInput,'05/05/2005');
            awaittestUtils.controlPanel.applyFilter(cfi);
            assert.containsNone(document.body,'.datepicker');
            cfi.destroy();
        });


        QUnit.module('DateTimePicker');

        QUnit.test("basicrendering",asyncfunction(assert){
            assert.expect(11);

            constpicker=awaitcreateComponent(DateTimePicker,{
                props:{date:moment('01/09/199712:30:01')},
            });

            assert.containsOnce(picker,'input.o_input.o_datepicker_input');
            assert.containsOnce(picker,'span.o_datepicker_button');
            assert.containsNone(document.body,'div.bootstrap-datetimepicker-widget');

            constinput=picker.el.querySelector('input.o_input.o_datepicker_input');
            assert.strictEqual(input.value,'01/09/199712:30:01',"Valueshouldbetheonegiven");
            assert.strictEqual(input.dataset.target,`#${picker.el.id}`,
                "DateTimePickeridshouldmatchitsinputtarget");

            awaittestUtils.dom.click(input);

            assert.containsOnce(document.body,'div.bootstrap-datetimepicker-widget.datepicker');
            assert.containsOnce(document.body,'div.bootstrap-datetimepicker-widget.timepicker');
            assert.strictEqual(
                document.querySelector('.datepicker.day.active').dataset.day,
                '01/09/1997',
                "Datepickershouldhavesetthecorrectday");

            assert.strictEqual(document.querySelector('.timepicker.timepicker-hour').innerText.trim(),'12',
                "Datepickershouldhavesetthecorrecthour");
            assert.strictEqual(document.querySelector('.timepicker.timepicker-minute').innerText.trim(),'30',
                "Datepickershouldhavesetthecorrectminute");
            assert.strictEqual(document.querySelector('.timepicker.timepicker-second').innerText.trim(),'01',
                "Datepickershouldhavesetthecorrectsecond");

            picker.destroy();
        });

        QUnit.test("pickadateandtime",asyncfunction(assert){
            assert.expect(5);

            constpicker=awaitcreateComponent(DateTimePicker,{
                props:{date:moment('01/09/199712:30:01')},
                intercepts:{
                    'datetime-changed':ev=>{
                        assert.step('datetime-changed');
                        assert.strictEqual(ev.detail.date.format('MM/DD/YYYYHH:mm:ss'),'02/08/199715:45:05',
                            "Eventshouldtransmitthecorrectdate");
                    },
                }
            });
            constinput=picker.el.querySelector('input.o_input.o_datepicker_input');

            awaittestUtils.dom.click(input);
            awaittestUtils.dom.click(document.querySelector('.datepickerth.next'));//February
            awaittestUtils.dom.click(document.querySelectorAll('.datepickertabletd')[15]);//08
            awaittestUtils.dom.click(document.querySelector('a[title="SelectTime"]'));
            awaittestUtils.dom.click(document.querySelector('.timepicker.timepicker-hour'));
            awaittestUtils.dom.click(document.querySelectorAll('.timepicker.hour')[15]);//15h
            awaittestUtils.dom.click(document.querySelector('.timepicker.timepicker-minute'));
            awaittestUtils.dom.click(document.querySelectorAll('.timepicker.minute')[9]);//45m
            awaittestUtils.dom.click(document.querySelector('.timepicker.timepicker-second'));

            assert.verifySteps([]);

            awaittestUtils.dom.click(document.querySelectorAll('.timepicker.second')[1]);//05s

            assert.strictEqual(input.value,'02/08/199715:45:05');
            assert.verifySteps(['datetime-changed']);

            picker.destroy();
        });

        QUnit.test("pickadateandtimewithlocale",asyncfunction(assert){
            assert.expect(5);

            //weirdshitofmomenthttps://github.com/moment/moment/issues/5600
            //Whenmonthregexreturnsundefined,januaryistaken(firstmonthofthedefault"nameless"locale)
            constoriginalLocale=moment.locale();
            //ThoseparameterswillmakeMoment'sinternalcomputestuffthatarerelevanttothebug
            constmonths='janvier_février_mars_avril_mai_juin_juillet_août_septembre_octobre_novembre_décembre'.split('_');
            constmonthsShort='janv._févr._mars_avr._mai_juin_juil._août_custSept._oct._nov._déc.'.split('_');
            moment.defineLocale('frenchForTests',{months,monthsShort,code:'frTest',monthsParseExact:true});

            consthasChanged=testUtils.makeTestPromise();
            constpicker=awaitcreateComponent(DateTimePicker,{
                translateParameters:{
                    date_format:"%d%b,%Y",//Thoseareimportanttoo
                    time_format:"%H:%M:%S",
                },
                props:{date:moment('09/01/199712:30:01','MM/DD/YYYYHH:mm:ss')},
                intercepts:{
                    'datetime-changed':ev=>{
                        assert.step('datetime-changed');
                        assert.strictEqual(ev.detail.date.format('MM/DD/YYYYHH:mm:ss'),'09/02/199715:45:05',
                            "Eventshouldtransmitthecorrectdate");
                        hasChanged.resolve();
                    },
                }
            });

            constinput=picker.el.querySelector('input.o_input.o_datepicker_input');

            awaittestUtils.dom.click(input);
            awaittestUtils.dom.click(document.querySelectorAll('.datepickertabletd')[3]);//nextday
            awaittestUtils.dom.click(document.querySelector('a[title="SelectTime"]'));
            awaittestUtils.dom.click(document.querySelector('.timepicker.timepicker-hour'));
            awaittestUtils.dom.click(document.querySelectorAll('.timepicker.hour')[15]);//15h
            awaittestUtils.dom.click(document.querySelector('.timepicker.timepicker-minute'));
            awaittestUtils.dom.click(document.querySelectorAll('.timepicker.minute')[9]);//45m
            awaittestUtils.dom.click(document.querySelector('.timepicker.timepicker-second'));

            assert.verifySteps([]);
            awaittestUtils.dom.click(document.querySelectorAll('.timepicker.second')[1]);//05s

            assert.strictEqual(input.value,'02custSept.,199715:45:05');
            assert.verifySteps(['datetime-changed']);

            awaithasChanged;

            moment.locale(originalLocale);
            moment.updateLocale('frenchForTests',null);

            picker.destroy();
        });

        QUnit.test("enteradatetimevalue",asyncfunction(assert){
            assert.expect(9);

            constpicker=awaitcreateComponent(DateTimePicker,{
                props:{date:moment('01/09/199712:30:01')},
                intercepts:{
                    'datetime-changed':ev=>{
                        assert.step('datetime-changed');
                        assert.strictEqual(ev.detail.date.format('MM/DD/YYYYHH:mm:ss'),'02/08/199715:45:05',
                            "Eventshouldtransmitthecorrectdate");
                    },
                }
            });
            constinput=picker.el.querySelector('.o_datepicker_input');

            assert.verifySteps([]);

            awaittestUtils.fields.editAndTrigger(input,'02/08/199715:45:05',['change']);

            assert.verifySteps(['datetime-changed']);

            awaittestUtils.dom.click(input);

            assert.strictEqual(input.value,'02/08/199715:45:05');
            assert.strictEqual(
                document.querySelector('.datepicker.day.active').dataset.day,
                '02/08/1997',
                "Datepickershouldhavesetthecorrectday"
            );
            assert.strictEqual(document.querySelector('.timepicker.timepicker-hour').innerText.trim(),'15',
                "Datepickershouldhavesetthecorrecthour");
            assert.strictEqual(document.querySelector('.timepicker.timepicker-minute').innerText.trim(),'45',
                "Datepickershouldhavesetthecorrectminute");
            assert.strictEqual(document.querySelector('.timepicker.timepicker-second').innerText.trim(),'05',
                "Datepickershouldhavesetthecorrectsecond");

            picker.destroy();
        });

        QUnit.test("Datetimeformatiscorrectlyset",asyncfunction(assert){
            assert.expect(2);

            testUtils.patch(time,{getLangDatetimeFormat:()=>"hh:mm:ssYYYY/MM/DD"});
            constpicker=awaitcreateComponent(DateTimePicker,{
                props:{date:moment('01/09/199712:30:01')},
            });
            constinput=picker.el.querySelector('.o_datepicker_input');

            assert.strictEqual(input.value,'12:30:011997/01/09');

            //Forcesanupdatetoassertthattheregisteredformatisthecorrectone
            awaittestUtils.dom.click(input);

            assert.strictEqual(input.value,'12:30:011997/01/09');

            picker.destroy();
            testUtils.unpatch(time);
        });
    });
});
