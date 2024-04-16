flectra.define('web_editor.field_html_tests',function(require){
"usestrict";

varajax=require('web.ajax');
varFormView=require('web.FormView');
vartestUtils=require('web.test_utils');
varweTestUtils=require('web_editor.test_utils');
varcore=require('web.core');
varWysiwyg=require('web_editor.wysiwyg');
varMediaDialog=require('wysiwyg.widgets.MediaDialog');
varFieldHtml=require('web_editor.field.html');
varFieldManagerMixin=require('web.FieldManagerMixin');

var_t=core._t;

QUnit.module('web_editor',{},function(){

    QUnit.module('fieldhtml',{
        beforeEach:function(){
            this.data=weTestUtils.wysiwygData({
                'note.note':{
                    fields:{
                        display_name:{
                            string:"Displayedname",
                            type:"char"
                        },
                        header:{
                            string:"Header",
                            type:"html",
                            required:true,
                        },
                        body:{
                            string:"Message",
                            type:"html"
                        },
                    },
                    records:[{
                        id:1,
                        display_name:"firstrecord",
                        header:"<p> &nbsp;&nbsp; <br>  </p>",
                        body:"<p>totototototo</p><p>tata</p>",
                    },{
                        id:2,
                        display_name:"secondrecord",
                        header:"<p> &nbsp;&nbsp; <br>  </p>",
                        body:`
<divclass="o_form_sheet_bg">
  <divclass="clearfixposition-relativeo_form_sheet"style="width:1140px;">
    <divclass="o_notebook">
      <divclass="tab-content">
        <divclass="tab-paneactive"id="notebook_page_820">
          <divclass="oe_form_fieldoe_form_field_htmlo_field_widget"name="description"style="margin-bottom:5px;">
            hackycodetotest
          </div>
        </div>
      </div>
    </div>
  </div>
</div>`,
                    }],
                },
                'mail.compose.message':{
                    fields:{
                        display_name:{
                            string:"Displayedname",
                            type:"char"
                        },
                        body:{
                            string:"MessageBodyinline(tosend)",
                            type:"html"
                        },
                        attachment_ids:{
                            string:"Attachments",
                            type:"many2many",
                            relation:"ir.attachment",
                        }
                    },
                    records:[{
                        id:1,
                        display_name:"SomeComposer",
                        body:"Hello",
                        attachment_ids:[],
                    }],
                },
                'mass.mailing':{
                    fields:{
                        display_name:{
                            string:"Displayedname",
                            type:"char"
                        },
                        body_html:{
                            string:"MessageBodyinline(tosend)",
                            type:"html"
                        },
                        body_arch:{
                            string:"MessageBodyforedition",
                            type:"html"
                        },
                    },
                    records:[{
                        id:1,
                        display_name:"firstrecord",
                        body_html:"<divclass='field_body'style='background-color:red;'>yep</div>",
                        body_arch:"<divclass='field_body'>yep</div>",
                    }],
                },
                "ir.translation":{
                    fields:{
                        lang_code:{type:"char"},
                        value:{type:"char"},
                        res_id:{type:"integer"}
                    },
                    records:[{
                        id:99,
                        res_id:12,
                        value:'',
                        lang_code:'en_US'
                    }]
                },
            });

            testUtils.mock.patch(ajax,{
                loadAsset:function(xmlId){
                    if(xmlId==='template.assets'){
                        returnPromise.resolve({
                            cssLibs:[],
                            cssContents:['body{background-color:red;}']
                        });
                    }
                    if(xmlId==='template.assets_all_style'){
                        returnPromise.resolve({
                            cssLibs:$('link[href]:not([type="image/x-icon"])').map(function(){
                                return$(this).attr('href');
                            }).get(),
                            cssContents:['body{background-color:red;}']
                        });
                    }
                    throw'Wrongtemplate';
                },
            });
        },
        afterEach:function(){
            testUtils.mock.unpatch(ajax);
        },
    },function(){

        QUnit.module('basic');

        QUnit.test('simplerendering',asyncfunction(assert){
            assert.expect(3);

            varform=awaittestUtils.createView({
                View:FormView,
                model:'note.note',
                data:this.data,
                arch:'<form>'+
                    '<fieldname="body"widget="html"style="height:100px"/>'+
                    '</form>',
                res_id:1,
            });
            var$field=form.$('.oe_form_field[name="body"]');
            assert.strictEqual($field.children('.o_readonly').html(),
                '<p>totototototo</p><p>tata</p>',
                "shouldhaverenderedadivwithcorrectcontentinreadonly");
            assert.strictEqual($field.attr('style'),'height:100px',
                "shouldhaveappliedthestylecorrectly");

            awaittestUtils.form.clickEdit(form);
            awaittestUtils.nextTick();
            $field=form.$('.oe_form_field[name="body"]');
            assert.strictEqual($field.find('.note-editable').html(),
                '<p>totototototo</p><p>tata</p>',
                "shouldhaverenderedthefieldcorrectlyinedit");

            form.destroy();
        });

        QUnit.test('notebooksdefinedinsideHTMLfieldwidgetsareignoredwhencallingsetLocalState',asyncfunction(assert){
            assert.expect(1);

            varform=awaittestUtils.createView({
                View:FormView,
                model:'note.note',
                data:this.data,
                arch:'<form>'+
                    '<fieldname="body"widget="html"style="height:100px"/>'+
                    '</form>',
                res_id:2,
            });
            //checkthatthereisnoerroronclickingEdit
            awaittestUtils.form.clickEdit(form);
            awaittestUtils.nextTick();
            assert.containsOnce(form,'.o_form_editable');

            form.destroy();
        });

        QUnit.test('checkifrequiredfieldisset',asyncfunction(assert){
            assert.expect(1);

            varform=awaittestUtils.createView({
                View:FormView,
                model:'note.note',
                data:this.data,
                arch:'<form>'+
                        '<fieldname="header"widget="html"style="height:100px"/>'+
                      '</form>',
                res_id:1,
            });

            testUtils.mock.intercept(form,'call_service',function(ev){
                if(ev.data.service==='notification'){
                    assert.deepEqual(ev.data.args[0],{
                        "className":undefined,
                        "message":"<ul><li>Header</li></ul>",
                        "sticky":undefined,
                        "title":"Invalidfields:",
                        "type":"danger"
                      });
                }
            },true);

            awaittestUtils.form.clickEdit(form);
            awaittestUtils.nextTick();
            awaittestUtils.dom.click(form.$('.o_form_button_save'));

            form.destroy();
        });

        QUnit.test('colorpicker',asyncfunction(assert){
            assert.expect(6);

            varform=awaittestUtils.createView({
                View:FormView,
                model:'note.note',
                data:this.data,
                arch:'<form>'+
                    '<fieldname="body"widget="html"style="height:100px"/>'+
                    '</form>',
                res_id:1,
            });

            //SummernoteneedsaRootWidgettosetasparentoftheColorPaletteWidget.Inthe
            //tests,thereisnoRootWidget,sowesetitheretotheparentoftheformview,which
            //canactasRootWidget,asitwillhonorrpcrequestscorrectly(totheMockServer).
            constrootWidget=flectra.__DEBUG__.services['root.widget'];
            flectra.__DEBUG__.services['root.widget']=form.getParent();

            awaittestUtils.form.clickEdit(form);
            var$field=form.$('.oe_form_field[name="body"]');

            //selectthetext
            varpText=$field.find('.note-editablep').first().contents()[0];
            Wysiwyg.setRange(pText,1,pText,10);
            //textisselected

            varrange=Wysiwyg.getRange($field[0]);
            assert.strictEqual(range.sc,pText,
                "shouldselectthetext");

            asyncfunctionopenColorpicker(selector){
                const$colorpicker=$field.find(selector);
                constopeningProm=newPromise(resolve=>{
                    $colorpicker.one('shown.bs.dropdown',()=>resolve());
                });
                awaittestUtils.dom.click($colorpicker.find('button:first'));
                returnopeningProm;
            }

            awaitopenColorpicker('.note-toolbar.note-back-color-preview');
            assert.ok($field.find('.note-back-color-preview').hasClass('show'),
                "shoulddisplaythecolorpicker");

            awaittestUtils.dom.click($field.find('.note-toolbar.note-back-color-preview.o_we_color_btn[style="background-color:#00FFFF;"]'));

            assert.ok(!$field.find('.note-back-color-preview').hasClass('show'),
                "shouldclosethecolorpicker");

            assert.strictEqual($field.find('.note-editable').html(),
                '<p>t<fontstyle="background-color:rgb(0,255,255);">otototo&nbsp;</font>toto</p><p>tata</p>',
                "shouldhaverenderedthefieldcorrectlyinedit");

            varfontContent=$field.find('.note-editablefont').contents()[0];
            varrangeControl={
                sc:fontContent,
                so:0,
                ec:fontContent,
                eo:fontContent.length,
            };
            range=Wysiwyg.getRange($field[0]);
            assert.deepEqual(_.pick(range,'sc','so','ec','eo'),rangeControl,
                "shouldselectthetextaftercolorchange");

            //selectthetext
            pText=$field.find('.note-editablep').first().contents()[2];
            Wysiwyg.setRange(fontContent,5,pText,2);
            //textisselected

            awaitopenColorpicker('.note-toolbar.note-back-color-preview');
            awaittestUtils.dom.click($field.find('.note-toolbar.note-back-color-preview.o_we_color_btn.bg-o-color-3'));

            assert.strictEqual($field.find('.note-editable').html(),
                '<p>t<fontstyle="background-color:rgb(0,255,255);">otot</font><fontstyle=""class="bg-o-color-3">oto&nbsp;</font><fontclass="bg-o-color-3"style="">to</font>to</p><p>tata</p>',
                "shouldhaverenderedthefieldcorrectlyinedit");

            flectra.__DEBUG__.services['root.widget']=rootWidget;
            form.destroy();
        });

    QUnit.test('mediadialog:upload',asyncfunction(assert){
            /**
             *Ensures_onAttachmentChangefromFieldHTMLiscalledonfileupload
             *aswellas_onFieldChangedwhenthatmodelisamailcomposer
             */
            assert.expect(2);
            constonAttachmentChangeTriggered=testUtils.makeTestPromise();
            testUtils.mock.patch(FieldHtml,{
                '_onAttachmentChange':function(ev){
                    this._super(ev);
                    onAttachmentChangeTriggered.resolve(true);
                }
            });

            constonRecordChange=testUtils.makeTestPromise();
            testUtils.mock.patch(FieldManagerMixin,{
                '_applyChanges':function(dataPointID,changes,event){
                    constres=this._super(dataPointID,changes,event);
                    onRecordChange.resolve(true);
                    returnres;
                },
            })

            constform=awaittestUtils.createView({
                View:FormView,
                model:'mail.compose.message',
                data:this.data,
                arch:'<form>'+
                    '<fieldname="body"widget="html"style="height:100px"/>'+
                    '<fieldname="attachment_ids"widget="many2many_binary"/>'+
                    '</form>',
                res_id:1,
                mockRPC:function(route,args){
                    if(args.model==='ir.attachment'){
                        if(args.method==="generate_access_token"){
                            returnPromise.resolve();
                        }
                    }
                    if(route.indexOf('/web/image/123/transparent.png')===0){
                        returnPromise.resolve();
                    }
                    if(route.indexOf('/web_unsplash/fetch_images')===0){
                        returnPromise.resolve();
                    }
                    if(route.indexOf('/web_editor/media_library_search')===0){
                        returnPromise.resolve();
                    }
                    if(route.indexOf('/web_editor/attachment/add_data')===0){
                        returnPromise.resolve({"id":5,"name":"test.jpg","description":false,"mimetype":"image/jpeg","checksum":"7951a43bbfb08fd742224ada280913d1897b89ab",
                                                "url":false,"type":"binary","res_id":1,"res_model":"note.note","public":false,"access_token":false,
                                                "image_src":"/web/image/1-a0e63e61/test.jpg","image_width":1,"image_height":1,"original_id":false
                                                });
                        }
                    returnthis._super(route,args);
                },
            });
            awaittestUtils.form.clickEdit(form);
            const$field=form.$('.oe_form_field[name="body"]');

            //initmockfiledata
            constfileB64='/9j/4AAQSkZJRgABAQEAYABgAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/2wBDAQkJCQwLDBgNDRgyIRwhMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjL/wAARCAABAAEDASIAAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtRAAAgEDAwIEAwUFBAQAAAF9AQIDAAQRBRIhMUEGE1FhByJxFDKBkaEII0KxwRVS0fAkM2JyggkKFhcYGRolJicoKSo0NTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqDhIWGh4iJipKTlJWWl5iZmqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uHi4+Tl5ufo6erx8vP09fb3+Pn6/8QAHwEAAwEBAQEBAQEBAQAAAAAAAAECAwQFBgcICQoL/8QAtREAAgECBAQDBAcFBAQAAQJ3AAECAxEEBSExBhJBUQdhcRMiMoEIFEKRobHBCSMzUvAVYnLRChYkNOEl8RcYGRomJygpKjU2Nzg5OkNERUZHSElKU1RVVldYWVpjZGVmZ2hpanN0dXZ3eHl6goOEhYaHiImKkpOUlZaXmJmaoqOkpaanqKmqsrO0tba3uLm6wsPExcbHyMnK0tPU1dbX2Nna4uPk5ebn6Onq8vP09fb3+Pn6/9oADAMBAAIRAxEAPwD3+iiigD//2Q==';
            constfileBytes=newUint8Array(atob(fileB64).split('').map(char=>char.charCodeAt(0)));

            //thedialogloadsomexmlassets
            constdefMediaDialog=testUtils.makeTestPromise();
            testUtils.mock.patch(MediaDialog,{
                init:function(){
                    this._super.apply(this,arguments);
                    this.opened(defMediaDialog.resolve.bind(defMediaDialog));
                    this.opened(()=>{
                        constinput=this.activeWidget.$fileInput.get(0);
                        Object.defineProperty(input,'files',{
                            value:[newFile(fileBytes,"test.jpg",{type:'image/jpeg'})],
                        });
                        this.activeWidget._onFileInputChange();
                        })
                },
            });

            constpText=$field.find('.note-editablep').first().contents()[0];
            Wysiwyg.setRange(pText,1);

            awaittestUtils.dom.click($field.find('.note-toolbar.note-insertbutton:has(.fa-file-image-o)'));

            //loadstaticxmlfile(dialog,mediadialog,unsplashimagewidget)
            awaitdefMediaDialog;

            assert.ok(awaitPromise.race([onAttachmentChangeTriggered,newPromise((res,_)=>setTimeout(()=>res(false),400))]),
                      "_onAttachmentChangewasnotcalledwiththenewattachment,necessaryforunsuseduploadcleanuponbackend");

            awaitonRecordChange;
            //waittocheckthatdomisproperlyupdated
            awaitnewPromise((res,_)=>setTimeout(()=>res(false),400));
            assert.ok(form.$('.o_attachment[title="test.jpg"]')[0])

            testUtils.mock.unpatch(MediaDialog);
            testUtils.mock.unpatch(FieldHtml);
            testUtils.mock.unpatch(FieldManagerMixin);
            form.destroy();

        });

        QUnit.test('mediadialog:image',asyncfunction(assert){
            assert.expect(1);

            varform=awaittestUtils.createView({
                View:FormView,
                model:'note.note',
                data:this.data,
                arch:'<form>'+
                    '<fieldname="body"widget="html"style="height:100px"/>'+
                    '</form>',
                res_id:1,
                mockRPC:function(route,args){
                    if(args.model==='ir.attachment'){
                        if(args.method==="generate_access_token"){
                            returnPromise.resolve();
                        }
                    }
                    if(route.indexOf('/web/image/123/transparent.png')===0){
                        returnPromise.resolve();
                    }
                    if(route.indexOf('/web_unsplash/fetch_images')===0){
                        returnPromise.resolve();
                    }
                    if(route.indexOf('/web_editor/media_library_search')===0){
                        returnPromise.resolve();
                    }
                    returnthis._super(route,args);
                },
            });
            awaittestUtils.form.clickEdit(form);
            var$field=form.$('.oe_form_field[name="body"]');

            //thedialogloadsomexmlassets
            vardefMediaDialog=testUtils.makeTestPromise();
            testUtils.mock.patch(MediaDialog,{
                init:function(){
                    this._super.apply(this,arguments);
                    this.opened(defMediaDialog.resolve.bind(defMediaDialog));
                }
            });

            varpText=$field.find('.note-editablep').first().contents()[0];
            Wysiwyg.setRange(pText,1);

            awaittestUtils.dom.click($field.find('.note-toolbar.note-insertbutton:has(.fa-file-image-o)'));

            //loadstaticxmlfile(dialog,mediadialog,unsplashimagewidget)
            awaitdefMediaDialog;

            awaittestUtils.dom.click($('.modal#editor-media-image.o_existing_attachment_cell:first').removeClass('d-none'));

            var$editable=form.$('.oe_form_field[name="body"].note-editable');
            assert.ok($editable.find('img')[0].dataset.src.includes('/web/image/123/transparent.png'),
                "shouldhavetheimageinthedom");

            testUtils.mock.unpatch(MediaDialog);

            form.destroy();
        });

        QUnit.test('mediadialog:icon',asyncfunction(assert){
            assert.expect(1);

            varform=awaittestUtils.createView({
                View:FormView,
                model:'note.note',
                data:this.data,
                arch:'<form>'+
                    '<fieldname="body"widget="html"style="height:100px"/>'+
                    '</form>',
                res_id:1,
                mockRPC:function(route,args){
                    if(args.model==='ir.attachment'){
                        returnPromise.resolve([]);
                    }
                    if(route.indexOf('/web_unsplash/fetch_images')===0){
                        returnPromise.resolve();
                    }
                    returnthis._super(route,args);
                },
            });
            awaittestUtils.form.clickEdit(form);
            var$field=form.$('.oe_form_field[name="body"]');

            //thedialogloadsomexmlassets
            vardefMediaDialog=testUtils.makeTestPromise();
            testUtils.mock.patch(MediaDialog,{
                init:function(){
                    this._super.apply(this,arguments);
                    this.opened(defMediaDialog.resolve.bind(defMediaDialog));
                }
            });

            varpText=$field.find('.note-editablep').first().contents()[0];
            Wysiwyg.setRange(pText,1);

            awaittestUtils.dom.click($field.find('.note-toolbar.note-insertbutton:has(.fa-file-image-o)'));

            //loadstaticxmlfile(dialog,mediadialog,unsplashimagewidget)
            awaitdefMediaDialog;
            $('.modal.tab-content.tab-pane').removeClass('fade');//tobesyncintest
            awaittestUtils.dom.click($('.modala[aria-controls="editor-media-icon"]'));
            awaittestUtils.dom.click($('.modal#editor-media-icon.font-icons-icon.fa-glass'));

            var$editable=form.$('.oe_form_field[name="body"].note-editable');

            assert.strictEqual($editable.data('wysiwyg').getValue(),
                '<p>t<spanclass="fafa-glass"></span>otototototo</p><p>tata</p>',
                "shouldhavetheimageinthedom");

            testUtils.mock.unpatch(MediaDialog);

            form.destroy();
        });

        QUnit.test('save',asyncfunction(assert){
            assert.expect(1);

            varform=awaittestUtils.createView({
                View:FormView,
                model:'note.note',
                data:this.data,
                arch:'<form>'+
                    '<fieldname="body"widget="html"style="height:100px"/>'+
                    '</form>',
                res_id:1,
                mockRPC:function(route,args){
                    if(args.method==="write"){
                        assert.strictEqual(args.args[1].body,
                            '<p>t<fontclass="bg-o-color-3">otototo&nbsp;</font>toto</p><p>tata</p>',
                            "shouldsavethecontent");

                    }
                    returnthis._super.apply(this,arguments);
                },
            });
            awaittestUtils.form.clickEdit(form);
            var$field=form.$('.oe_form_field[name="body"]');

            //selectthetext
            varpText=$field.find('.note-editablep').first().contents()[0];
            Wysiwyg.setRange(pText,1,pText,10);
            //textisselected

            asyncfunctionopenColorpicker(selector){
                const$colorpicker=$field.find(selector);
                constopeningProm=newPromise(resolve=>{
                    $colorpicker.one('shown.bs.dropdown',()=>resolve());
                });
                awaittestUtils.dom.click($colorpicker.find('button:first'));
                returnopeningProm;
            }

            awaitopenColorpicker('.note-toolbar.note-back-color-preview');
            awaittestUtils.dom.click($field.find('.note-toolbar.note-back-color-preview.o_we_color_btn.bg-o-color-3'));

            awaittestUtils.form.clickSave(form);

            form.destroy();
        });

        QUnit.module('cssReadonly');

        QUnit.test('renderingwithiframeforreadonlymode',asyncfunction(assert){
            assert.expect(3);

            varform=awaittestUtils.createView({
                View:FormView,
                model:'note.note',
                data:this.data,
                arch:'<form>'+
                    '<fieldname="body"widget="html"style="height:100px"options="{\'cssReadonly\':\'template.assets\'}"/>'+
                    '</form>',
                res_id:1,
            });
            var$field=form.$('.oe_form_field[name="body"]');
            var$iframe=$field.find('iframe.o_readonly');
            await$iframe.data('loadDef');
            vardoc=$iframe.contents()[0];
            assert.strictEqual($(doc).find('#iframe_target').html(),
                '<p>totototototo</p><p>tata</p>',
                "shouldhaverenderedadivwithcorrectcontentinreadonly");

            assert.strictEqual(doc.defaultView.getComputedStyle(doc.body).backgroundColor,
                'rgb(255,0,0)',
                "shouldloadtheassetcss");

            awaittestUtils.form.clickEdit(form);

            $field=form.$('.oe_form_field[name="body"]');
            assert.strictEqual($field.find('.note-editable').html(),
                '<p>totototototo</p><p>tata</p>',
                "shouldhaverenderedthefieldcorrectlyinedit");

            form.destroy();
        });

        QUnit.module('translation');

        QUnit.test('fieldhtmltranslatable',asyncfunction(assert){
            assert.expect(4);

            varmultiLang=_t.database.multi_lang;
            _t.database.multi_lang=true;

            this.data['note.note'].fields.body.translate=true;

            varform=awaittestUtils.createView({
                View:FormView,
                model:'note.note',
                data:this.data,
                arch:'<formstring="Partners">'+
                    '<fieldname="body"widget="html"/>'+
                    '</form>',
                res_id:1,
                mockRPC:function(route,args){
                    if(route==='/web/dataset/call_button'&&args.method==='translate_fields'){
                        assert.deepEqual(args.args,['note.note',1,'body'],"shouldcall'call_button'route");
                        returnPromise.resolve({
                            domain:[],
                            context:{search_default_name:'partnes,foo'},
                        });
                    }
                    if(route==="/web/dataset/call_kw/res.lang/get_installed"){
                        returnPromise.resolve([["en_US"],["fr_BE"]]);
                    }
                    returnthis._super.apply(this,arguments);
                },
            });
            assert.strictEqual(form.$('.oe_form_field_html.o_field_translate').length,0,
                "shouldnothaveatranslatebuttoninreadonlymode");

            awaittestUtils.form.clickEdit(form);
            var$button=form.$('.oe_form_field_html.o_field_translate');
            assert.strictEqual($button.length,1,"shouldhaveatranslatebutton");
            awaittestUtils.dom.click($button);
            assert.containsOnce($(document),'.o_translation_dialog','shouldhaveamodaltotranslate');

            form.destroy();
            _t.database.multi_lang=multiLang;
        });
    });
});
});
