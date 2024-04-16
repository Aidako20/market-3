flectra.define('website_form_editor.tour',function(require){
    'usestrict';

    constrpc=require('web.rpc');
    consttour=require("web_tour.tour");

    constselectButtonByText=function(text){
        return[{
            content:"Opentheselect",
            trigger:`we-select:has(we-button:contains("${text}"))we-toggler`,
        },
        {
            content:"Clickontheoption",
            trigger:`we-selectwe-button:contains("${text}")`,
        }];
    };
    constselectButtonByData=function(data){
        return[{
            content:"Opentheselect",
            trigger:`we-select:has(we-button[${data}])we-toggler`,
        },{
            content:"Clickontheoption",
            trigger:`we-selectwe-button[${data}]`,
        }];
    };
    constaddField=function(data,name,type,label,required,hidden){
        constret=[{
            content:"Selectform",
            extra_trigger:'.s_website_form_field',
            trigger:'section.s_website_form',
        },{
            content:"Addfield",
            trigger:'we-button[data-add-field]',
        },
        ...selectButtonByData(data),
        {
            content:"Waitforfieldtoload",
            trigger:`.s_website_form_field[data-type="${name}"],.s_website_form_input[name="${name}"]`,//customorexistingfield
            run:function(){},
        }];
        lettestText='.s_website_form_field';
        if(required){
            testText+='.s_website_form_required';
            ret.push({
                content:"Markthefieldasrequired",
                trigger:'we-button[data-name="required_opt"]we-checkbox',
            });
        }
        if(hidden){
            testText+='.s_website_form_field_hidden';
            ret.push({
                content:"Markthefieldashidden",
                trigger:'we-button[data-name="hidden_opt"]we-checkbox',
            });
        }
        if(label){
            testText+=`:has(label:contains("${label}"))`;
            ret.push({
                content:"Changethelabeltext",
                trigger:'we-input[data-set-label-text]input',
                run:`text${label}`,
            });
        }
        if(type!=='checkbox'&&type!=='radio'&&type!=='select'){
            letinputType=type==='textarea'?type:`input[type="${type}"]`;
            testText+=`:has(${inputType}[name="${name}"]${required?'[required]':''})`;
        }
        ret.push({
            content:"Checktheresultingfield",
            trigger:testText,
            run:function(){},
        });
        returnret;
    };
    constaddCustomField=function(name,type,label,required,hidden){
        returnaddField(`data-custom-field="${name}"`,name,type,label,required,hidden);
    };
    constaddExistingField=function(name,type,label,required,hidden){
        returnaddField(`data-existing-field="${name}"`,name,type,label,required,hidden);
    };

    tour.register("website_form_editor_tour",{
        test:true,
    },[
        //Dropaformbuildersnippetandconfigureit
        {
            content:"Entereditmode",
            trigger:'a[data-action=edit]',
        },{
            content:"Droptheformsnippet",
            trigger:'#oe_snippets.oe_snippet:has(.s_website_form).oe_snippet_thumbnail',
            run:'drag_and_drop#wrap',
        },{
            content:"Selectformbyclickingonaninputfield",
            extra_trigger:'.s_website_form_field',
            trigger:'section.s_website_forminput',
        },{
            content:"Verifythattheformeditorappeared",
            trigger:'.o_we_customize_panel.snippet-option-WebsiteFormEditor',
            run:()=>null,
        },{
            content:"Gobacktoblockstounselectform",
            trigger:'.o_we_add_snippet_btn',
        },{
            content:"Selectformbyclickingonatextarea",
            extra_trigger:'.s_website_form_field',
            trigger:'section.s_website_formtextarea',
        },{
            content:"Verifythattheformeditorappeared",
            trigger:'.o_we_customize_panel.snippet-option-WebsiteFormEditor',
            run:()=>null,
        },{
            content:"Renamethefieldlabel",
            trigger:'we-input[data-set-label-text]input',
            run:"textRenamed",
        },{
            content:"Leavetherenameoptions",
            trigger:'we-input[data-set-label-text]input',
            run:"text_blur",
        },{
            content:"Gobacktoblockstounselectform",
            trigger:'.o_we_add_snippet_btn',
        },{
            content:"Selectformitself(notaspecificfield)",
            extra_trigger:'.s_website_form_field',
            trigger:'section.s_website_form',
        },
        ...selectButtonByText('SendanE-mail'),
        {
            content:"Formhasamodelname",
            trigger:'section.s_website_formform[data-model_name="mail.mail"]',
        },{
            content:"CompleteRecipientE-mail",
            trigger:'[data-field-name="email_to"]input',
            run:'text_blurtest@test.test',
        },
        ...addExistingField('date','text','TestDate',true),

        ...addExistingField('record_name','text','AwesomeLabel',false,true),

        ...addExistingField('body_html','textarea','YourMessage',true),

        ...addExistingField('recipient_ids','checkbox'),

        ...addCustomField('one2many','checkbox','Products',true),
        {
            content:"ChangeOption1label",
            trigger:'we-listtableinput:eq(0)',
            run:'textIphone',
        },{
            content:"ChangeOption2label",
            trigger:'we-listtableinput:eq(1)',
            run:'textGalaxyS',
        },{
            content:"ChangefirstOption3label",
            trigger:'we-listtableinput:eq(2)',
            run:'textXperia',
        },{
            content:"ClickonAddnewCheckbox",
            trigger:'we-listwe-button.o_we_list_add_optional',
        },{
            content:"ChangeaddedOptionlabel",
            trigger:'we-listtableinput:eq(3)',
            run:'textWikoStairway',
        },{
            content:"Checktheresultingfield",
            trigger:".s_website_form_field.s_website_form_custom.s_website_form_required"+
                        ":has(.s_website_form_multiple[data-display='horizontal'])"+
                        ":has(.checkbox:has(label:contains('Iphone')):has(input[type='checkbox'][required]))"+
                        ":has(.checkbox:has(label:contains('GalaxyS')):has(input[type='checkbox'][required]))"+
                        ":has(.checkbox:has(label:contains('Xperia')):has(input[type='checkbox'][required]))"+
                        ":has(.checkbox:has(label:contains('WikoStairway')):has(input[type='checkbox'][required]))",
            run:function(){},
        },
        ...selectButtonByData('data-multi-checkbox-display="vertical"'),
        {
            content:"Checktheresultingfield",
            trigger:".s_website_form_field.s_website_form_custom.s_website_form_required"+
                        ":has(.s_website_form_multiple[data-display='vertical'])"+
                        ":has(.checkbox:has(label:contains('Iphone')):has(input[type='checkbox'][required]))"+
                        ":has(.checkbox:has(label:contains('GalaxyS')):has(input[type='checkbox'][required]))"+
                        ":has(.checkbox:has(label:contains('Xperia')):has(input[type='checkbox'][required]))"+
                        ":has(.checkbox:has(label:contains('WikoStairway')):has(input[type='checkbox'][required]))",
            run:function(){},
        },

        ...addCustomField('selection','radio','Service',true),
        {
            content:"ChangeOption1label",
            trigger:'we-listtableinput:eq(0)',
            run:'textAfter-salesService',
        },{
            content:"ChangeOption2label",
            trigger:'we-listtableinput:eq(1)',
            run:'textInvoicingService',
        },{
            content:"ChangefirstOption3label",
            trigger:'we-listtableinput:eq(2)',
            run:'textDevelopmentService',
        },{
            content:"ClickonAddnewCheckbox",
            trigger:'we-listwe-button.o_we_list_add_optional',
        },{
            content:"ChangelastOptionlabel",
            trigger:'we-listtableinput:eq(3)',
            run:'textManagementService',
        },{
            content:"Markthefieldasnotrequired",
            trigger:'we-button[data-name="required_opt"]we-checkbox',
        },{
            content:"Checktheresultingfield",
            trigger:".s_website_form_field.s_website_form_custom:not(.s_website_form_required)"+
                        ":has(.radio:has(label:contains('After-salesService')):has(input[type='radio']:not([required])))"+
                        ":has(.radio:has(label:contains('InvoicingService')):has(input[type='radio']:not([required])))"+
                        ":has(.radio:has(label:contains('DevelopmentService')):has(input[type='radio']:not([required])))"+
                        ":has(.radio:has(label:contains('ManagementService')):has(input[type='radio']:not([required])))",
            run:function(){},
        },

        ...addCustomField('many2one','select','State',true),

        //Customizecustomselectionfield
        {
            content:"ChangeOption1Label",
            trigger:'we-listtableinput:eq(0)',
            run:'textGermany',
        },{
            content:"ChangeOption2Label",
            trigger:'we-listtableinput:eq(1)',
            run:'textBelgium',
        },{
            content:"ChangefirstOption3label",
            trigger:'we-listtableinput:eq(2)',
            run:'textFrance',
        },{
            content:"ClickonAddnewCheckbox",
            trigger:'we-listwe-button.o_we_list_add_optional',
        },{
            content:"ChangelastOptionlabel",
            trigger:'we-listtableinput:eq(3)',
            run:'textCanada',
        },{
            content:"RemoveGermanyOption",
            trigger:'.o_we_select_remove_option:eq(0)',
        },{
            content:"Checktheresultingsnippet",
            trigger:".s_website_form_field.s_website_form_custom.s_website_form_required"+
                        ":has(label:contains('State'))"+
                        ":has(select[required]:hidden)"+
                        ":has(.s_website_form_select_item:contains('Belgium'))"+
                        ":has(.s_website_form_select_item:contains('France'))"+
                        ":has(.s_website_form_select_item:contains('Canada'))"+
                        ":not(:has(.s_website_form_select_item:contains('Germany')))",
            run:function(){},
        },

        ...addExistingField('attachment_ids','file','InvoiceScan'),

        //EditthesubmitbuttonusinglinkDialog.
        {
            content:"Doubleclicksubmitbuttontoeditit",
            trigger:'.s_website_form_send',
            run:'dblclick',
        },{
            content:"CheckthatnoURLfieldissuggested",
            trigger:'form:has(#o_link_dialog_label_input:hidden)',
            run:()=>null,
        },{
            content:"Checkthatpreviewelementhasthesamestyle",
            trigger:'.o_link_dialog_preview:has(.s_website_form_send.btn.btn-lg.btn-primary)',
            run:()=>null,
        },{
            content:"Changebutton'sstyle",
            trigger:'label:has(input[name="link_style_color"][value="secondary"])',
            run:()=>{
                $('input[name="link_style_color"][value="secondary"]').click();
                $('select[name="link_style_shape"]').val('rounded-circle').change();
                $('select[name="link_style_size"]').val('sm').change();
            },
        },{
            content:"Checkthatpreviewisupdatedtoo",
            trigger:'.o_link_dialog_preview:has(.s_website_form_send.btn.btn-sm.btn-secondary.rounded-circle)',
            run:()=>null,
        },{
            content:"SavechangesfromlinkDialog",
            trigger:'.modal-footer.btn-primary',
        },{
            content:"Checktheresultingbutton",
            trigger:'.s_website_form_send.btn.btn-sm.btn-secondary.rounded-circle',
            run:()=>null,
        },
        //Savethepage
        {
            trigger:'body',
            run:function(){
                $('body').append('<divid="completlyloaded"></div>');
            },
        },
        {
            content: "Savethepage",
            trigger: "button[data-action=save]",
        },
        {
            content: "Waitreloading...",
            trigger: "html:not(:has(#completlyloaded))div",
        }
    ]);

    tour.register("website_form_editor_tour_submit",{
        test:true,
    },[
        {
            content: "Trytosendemptyform",
            extra_trigger: "form[data-model_name='mail.mail']"+
                            "[data-success-page='/contactus-thank-you']"+
                            ":has(.s_website_form_field:has(label:contains('YourName')):has(input[type='text'][name='YourName'][required]))"+
                            ":has(.s_website_form_field:has(label:contains('Email')):has(input[type='email'][name='email_from'][required]))"+
                            ":has(.s_website_form_field:has(label:contains('YourQuestion')):has(textarea[name='YourQuestion'][required]))"+
                            ":has(.s_website_form_field:has(label:contains('Subject')):has(input[type='text'][name='subject'][required]))"+
                            ":has(.s_website_form_field:has(label:contains('TestDate')):has(input[type='text'][name='date'][required]))"+
                            ":has(.s_website_form_field:has(label:contains('AwesomeLabel')):hidden)"+
                            ":has(.s_website_form_field:has(label:contains('YourMessage')):has(textarea[name='body_html'][required]))"+
                            ":has(.s_website_form_field:has(label:contains('Products')):has(input[type='checkbox'][name='Products'][value='Iphone'][required]))"+
                            ":has(.s_website_form_field:has(label:contains('Products')):has(input[type='checkbox'][name='Products'][value='GalaxyS'][required]))"+
                            ":has(.s_website_form_field:has(label:contains('Products')):has(input[type='checkbox'][name='Products'][value='Xperia'][required]))"+
                            ":has(.s_website_form_field:has(label:contains('Products')):has(input[type='checkbox'][name='Products'][value='WikoStairway'][required]))"+
                            ":has(.s_website_form_field:has(label:contains('Service')):has(input[type='radio'][name='Service'][value='After-salesService']:not([required])))"+
                            ":has(.s_website_form_field:has(label:contains('Service')):has(input[type='radio'][name='Service'][value='InvoicingService']:not([required])))"+
                            ":has(.s_website_form_field:has(label:contains('Service')):has(input[type='radio'][name='Service'][value='DevelopmentService']:not([required])))"+
                            ":has(.s_website_form_field:has(label:contains('Service')):has(input[type='radio'][name='Service'][value='ManagementService']:not([required])))"+
                            ":has(.s_website_form_field:has(label:contains('State')):has(select[name='State'][required]:has(option[value='Belgium'])))"+
                            ":has(.s_website_form_field.s_website_form_required:has(label:contains('State')):has(select[name='State'][required]:has(option[value='France'])))"+
                            ":has(.s_website_form_field:has(label:contains('State')):has(select[name='State'][required]:has(option[value='Canada'])))"+
                            ":has(.s_website_form_field:has(label:contains('InvoiceScan')))"+
                            ":has(.s_website_form_field:has(input[name='email_to'][value='test@test.test']))"+
                            ":has(.s_website_form_field:has(input[name='website_form_signature']))",
            trigger: ".s_website_form_send"
        },
        {
            content: "CheckifrequiredfieldsweredetectedandcompletetheSubjectfield",
            extra_trigger: "form:has(#s_website_form_result.text-danger)"+
                            ":has(.s_website_form_field:has(label:contains('YourName')).o_has_error)"+
                            ":has(.s_website_form_field:has(label:contains('Email')).o_has_error)"+
                            ":has(.s_website_form_field:has(label:contains('YourQuestion')).o_has_error)"+
                            ":has(.s_website_form_field:has(label:contains('Subject')).o_has_error)"+
                            ":has(.s_website_form_field:has(label:contains('TestDate')).o_has_error)"+
                            ":has(.s_website_form_field:has(label:contains('YourMessage')).o_has_error)"+
                            ":has(.s_website_form_field:has(label:contains('Products')).o_has_error)"+
                            ":has(.s_website_form_field:has(label:contains('Service')):not(.o_has_error))"+
                            ":has(.s_website_form_field:has(label:contains('State')):not(.o_has_error))"+
                            ":has(.s_website_form_field:has(label:contains('InvoiceScan')):not(.o_has_error))",
            trigger: "input[name=subject]",
            run:     "textJaneSmith"
        },
        {
            content: "UpdaterequiredfieldstatusbytryingtoSendagain",
            trigger: ".s_website_form_send"
        },
        {
            content: "CheckifrequiredfieldsweredetectedandcompletetheMessagefield",
            extra_trigger: "form:has(#s_website_form_result.text-danger)"+
                            ":has(.s_website_form_field:has(label:contains('YourName')).o_has_error)"+
                            ":has(.s_website_form_field:has(label:contains('Email')).o_has_error)"+
                            ":has(.s_website_form_field:has(label:contains('YourQuestion')).o_has_error)"+
                            ":has(.s_website_form_field:has(label:contains('Subject')):not(.o_has_error))"+
                            ":has(.s_website_form_field:has(label:contains('TestDate')).o_has_error)"+
                            ":has(.s_website_form_field:has(label:contains('YourMessage')).o_has_error)"+
                            ":has(.s_website_form_field:has(label:contains('Products')).o_has_error)"+
                            ":has(.s_website_form_field:has(label:contains('Service')):not(.o_has_error))"+
                            ":has(.s_website_form_field:has(label:contains('State')):not(.o_has_error))"+
                            ":has(.s_website_form_field:has(label:contains('InvoiceScan')):not(.o_has_error))",
            trigger: "textarea[name=body_html]",
            run:     "textAuselessmessage"
        },
        {
            content: "UpdaterequiredfieldstatusbytryingtoSendagain",
            trigger: ".s_website_form_send"
        },
        {
            content: "Checkifrequiredfieldswasdetectedandcheckaproduct.Ifthisfails,youprobablybrokethecleanForSave.",
            extra_trigger: "form:has(#s_website_form_result.text-danger)"+
                            ":has(.s_website_form_field:has(label:contains('YourName')).o_has_error)"+
                            ":has(.s_website_form_field:has(label:contains('Email')).o_has_error)"+
                            ":has(.s_website_form_field:has(label:contains('YourQuestion')).o_has_error)"+
                            ":has(.s_website_form_field:has(label:contains('Subject')):not(.o_has_error))"+
                            ":has(.s_website_form_field:has(label:contains('TestDate')).o_has_error)"+
                            ":has(.s_website_form_field:has(label:contains('YourMessage')):not(.o_has_error))"+
                            ":has(.s_website_form_field:has(label:contains('Products')).o_has_error)"+
                            ":has(.s_website_form_field:has(label:contains('Service')):not(.o_has_error))"+
                            ":has(.s_website_form_field:has(label:contains('State')):not(.o_has_error))"+
                            ":has(.s_website_form_field:has(label:contains('InvoiceScan')):not(.o_has_error))",
            trigger: "input[name=Products][value='WikoStairway']"
        },
        {
            content: "CompleteDatefield",
            trigger: ".s_website_form_datetime[data-toggle='datetimepicker']",
        },
        {
            content: "Checkanotherproduct",
            trigger: "input[name='Products'][value='Xperia']"
        },
        {
            content: "Checkaservice",
            trigger: "input[name='Service'][value='DevelopmentService']"
        },
        {
            content: "CompleteYourNamefield",
            trigger: "input[name='YourName']",
            run:     "textchhagan"
        },
        {
            content: "CompleteEmailfield",
            trigger: "input[name=email_from]",
            run:     "texttest@mail.com"
        },
        {
            content:"CompleteSubjectfield",
            trigger:'input[name="subject"]',
            run:'textsubject',
        },
        {
            content: "CompleteYourQuestionfield",
            trigger: "textarea[name='YourQuestion']",
            run:     "textmagan"
        },
        {
            content: "Sendtheform",
            trigger: ".s_website_form_send"
        },
        {
            content: "Checkformissubmittedwithouterrors",
            trigger: "#wrap:has(h1:contains('ThankYou!'))"
        }
    ]);

    tour.register("website_form_editor_tour_results",{
        test:true,
    },[
        {
            content:"Checkmail.mailrecordshavebeencreated",
            trigger:"body",
            run:function(){
                varmailDef=rpc.query({
                        model:'mail.mail',
                        method:'search_count',
                        args:[[
                            ['email_to','=','test@test.test'],
                            ['body_html','like','Auselessmessage'],
                            ['body_html','like','Service:DevelopmentService'],
                            ['body_html','like','State:Belgium'],
                            ['body_html','like','Products:Xperia,WikoStairway']
                        ]],
                    });
                varsuccess=function(model,count){
                    if(count>0){
                        $('body').append('<divid="website_form_editor_success_test_tour_'+model+'"></div>');
                    }
                };
                mailDef.then(_.bind(success,this,'mail_mail'));
            }
        },
        {
            content: "Checkmail.mailrecordshavebeencreated",
            trigger: "#website_form_editor_success_test_tour_mail_mail"
        }
    ]);

    return{};
});
