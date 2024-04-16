flectra.define('sms.sms_widget_tests',function(require){
"usestrict";

varconfig=require('web.config');
varFormView=require('web.FormView');
varListView=require('web.ListView');
vartestUtils=require('web.test_utils');

varcreateView=testUtils.createView;

QUnit.module('fields',{
    beforeEach:function(){
        this.data={
            partner:{
                fields:{
                    message:{string:"message",type:"text"},
                    foo:{string:"Foo",type:"char",default:"MylittleFooValue"},
                    mobile:{string:"mobile",type:"text"},
                },
                records:[{
                    id:1,
                    message:"",
                    foo:'yop',
                    mobile:"+32494444444",
                },{
                    id:2,
                    message:"",
                    foo:'bayou',
                }]
            },
            visitor:{
                fields:{
                    mobile:{string:"mobile",type:"text"},
                },
                records:[{
                    id:1,
                    mobile:"+32494444444",
                }]
            },
        };
    }
},function(){

    QUnit.module('SmsWidget');

    QUnit.test('Smswidgetsarecorrectlyrendered',asyncfunction(assert){
        assert.expect(9);
        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<form><sheet><fieldname="message"widget="sms_widget"/></sheet></form>',
        });

        assert.containsOnce(form,'.o_sms_count',"Shouldhaveasmscounter");
        assert.strictEqual(form.$('.o_sms_count').text(),'0characters,fitsin0SMS(GSM7)',
            'Shouldbe"0characters,fitsin0SMS(GSM7)"bydefault');
        //GSM-7
        awaittestUtils.fields.editAndTrigger(form.$('.o_input'),"HellofromFlectra",'input');
        assert.strictEqual(form.$('.o_sms_count').text(),'15characters,fitsin1SMS(GSM7)',
            'Shouldbe"15characters,fitsin1SMS(GSM7)"for"HellofromFlectra"');
        //GSM-7with\n=>thisonecountas2characters
        form.$('.o_input').val("HellofromFlectra\n").trigger('input');
        assert.strictEqual(form.$('.o_sms_count').text(),'17characters,fitsin1SMS(GSM7)',
            'Shouldbe"17characters,fitsin1SMS(GSM7)"for"HellofromFlectra\\n"');
        //Unicode=>ê
        form.$('.o_input').val("HêllofromFlectra").trigger('input');
        assert.strictEqual(form.$('.o_sms_count').text(),'15characters,fitsin1SMS(UNICODE)',
            'Shouldbe"15characters,fitsin1SMS(UNICODE)"for"HêllofromFlectra"');
        //GSM-7with160c
        vartext=Array(161).join('a');
        awaittestUtils.fields.editAndTrigger(form.$('.o_input'),text,'input');
        assert.strictEqual(form.$('.o_sms_count').text(),'160characters,fitsin1SMS(GSM7)',
            'Shouldbe"160characters,fitsin1SMS(GSM7)"for160x"a"');
        //GSM-7with161c
        text=Array(162).join('a');
        awaittestUtils.fields.editAndTrigger(form.$('.o_input'),text,'input');
        assert.strictEqual(form.$('.o_sms_count').text(),'161characters,fitsin2SMS(GSM7)',
            'Shouldbe"161characters,fitsin2SMS(GSM7)"for161x"a"');
        //Unicodewith70c
        text=Array(71).join('ê');
        awaittestUtils.fields.editAndTrigger(form.$('.o_input'),text,'input');
        assert.strictEqual(form.$('.o_sms_count').text(),'70characters,fitsin1SMS(UNICODE)',
            'Shouldbe"70characters,fitsin1SMS(UNICODE)"for70x"ê"');
        //Unicodewith71c
        text=Array(72).join('ê');
        awaittestUtils.fields.editAndTrigger(form.$('.o_input'),text,'input');
        assert.strictEqual(form.$('.o_sms_count').text(),'71characters,fitsin2SMS(UNICODE)',
            'Shouldbe"71characters,fitsin2SMS(UNICODE)"for71x"ê"');

        form.destroy();
    });

    QUnit.test('Smswidgetswithnon-emptyinitialvalue',asyncfunction(assert){
        assert.expect(1);
        varform=awaitcreateView({
            View:FormView,
            model:'visitor',
            data:this.data,
            arch:`<form><sheet><fieldname="mobile"widget="sms_widget"/></sheet></form>`,
            res_id:1,
            res_ids:[1],
        });

        assert.strictEqual(form.$('.o_field_text').text(),'+32494444444',
            'Shouldhavetheinitialvalue');

        form.destroy();
    });

    QUnit.test('Smswidgetswithemptyinitialvalue',asyncfunction(assert){
        assert.expect(1);
        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:`<form><sheet><fieldname="message"widget="sms_widget"/></sheet></form>`,
            res_id:1,
            res_ids:[1],
        });

        assert.strictEqual(form.$('.o_field_text').text(),'',
            'Shouldhavetheemptyinitialvalue');

        form.destroy();
    });

    QUnit.module('PhoneWidget');

    QUnit.test('phonefieldineditablelistviewonnormalscreens',asyncfunction(assert){
        assert.expect(11);
        vardoActionCount=0;

        varlist=awaitcreateView({
            View:ListView,
            model:'partner',
            data:this.data,
            debug:true,
            arch:'<treeeditable="bottom"><fieldname="foo"widget="phone"/></tree>',
            intercepts:{
                do_action(ev){
                    assert.equal(ev.data.action.res_model,'sms.composer',
                        'TheactiontosendanSMSshouldhavebeenexecuted');
                    doActionCount+=1;
                }
            }
        });

        assert.containsN(list,'tbodytd:not(.o_list_record_selector)',4);
        assert.strictEqual(list.$('tbodytd:not(.o_list_record_selector)').first().text(),'yopSMS',
            "valueshouldbedisplayedproperlywithalinktosendSMS");

        assert.containsN(list,'a.o_field_widget.o_form_uri',2,
            "shouldhavethecorrectclassnames");

        //Editalineandchecktheresult
        var$cell=list.$('tbodytd:not(.o_list_record_selector)').first();
        awaittestUtils.dom.click($cell);
        assert.hasClass($cell.parent(),'o_selected_row','shouldbesetaseditmode');
        assert.strictEqual($cell.find('input').val(),'yop',
            'shouldhavethecorectvalueininternalinput');
        awaittestUtils.fields.editInput($cell.find('input'),'new');

        //save
        awaittestUtils.dom.click(list.$buttons.find('.o_list_button_save'));
        $cell=list.$('tbodytd:not(.o_list_record_selector)').first();
        assert.doesNotHaveClass($cell.parent(),'o_selected_row','shouldnotbeineditmodeanymore');
        assert.strictEqual(list.$('tbodytd:not(.o_list_record_selector)').first().text(),'newSMS',
            "valueshouldbeproperlyupdated");
        assert.containsN(list,'a.o_field_widget.o_form_uri',2,
            "shouldstillhavelinkswithcorrectclasses");

        awaittestUtils.dom.click(list.$('tbodytd:not(.o_list_record_selector).o_field_phone_sms').first());
        assert.equal(doActionCount,1,'Onlyoneactionshouldhavebeenexecuted');
        assert.containsNone(list,'.o_selected_row',
            'Noneofthelistelementshouldhavebeenactivated');

        list.destroy();
    });

    QUnit.test('readonlysmsphonefieldisproperlyrerenderedafterbeenchangedbyonchange',asyncfunction(assert){
        assert.expect(4);

        constNEW_PHONE='+32595555555';

        constform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                '<sheet>'+
                '<group>'+
                '<fieldname="foo"on_change="1"/>'+//onchangetoupdatemobileinreadonlymodedirectly
                '<fieldname="mobile"widget="phone"readonly="1"/>'+//readonlyonly,wedon'twanttogothroughwritemode
                '</group>'+
                '</sheet>'+
                '</form>',
            res_id:1,
            viewOptions:{mode:'edit'},
            mockRPC:function(route,args){
                if(args.method==='onchange'){
                    returnPromise.resolve({
                        value:{
                            mobile:NEW_PHONE,//onchangetoupdatemobileinreadonlymodedirectly
                        },
                    });
                }
                returnthis._super.apply(this,arguments);
            },
        });
        //checkinitialrendering
        assert.strictEqual(form.$('.o_field_phone').text(),"+32494444444",
                           'InitialPhonetextshouldbeset');
        assert.strictEqual(form.$('.o_field_phone_sms').text(),'SMS',
                           'SMSbuttonlabelshouldberendered');

        //triggertheonchangetoupdatephonefield,butstillinreadonlymode
        awaittestUtils.fields.editInput($('input[name="foo"]'),'someOtherFoo');

        //checkrenderingafterchanges
        assert.strictEqual(form.$('.o_field_phone').text(),NEW_PHONE,
                           'Phonetextshouldbeupdated');
        assert.strictEqual(form.$('.o_field_phone_sms').text(),'SMS',
                           'SMSbuttonlabelshouldnotbechanged');

        form.destroy();
    });
});
});
