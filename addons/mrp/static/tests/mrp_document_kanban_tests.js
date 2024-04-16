flectra.define('mrp.document_kanban_tests',function(require){
"usestrict";

constMrpDocumentsKanbanView=require('mrp.MrpDocumentsKanbanView');
constMrpDocumentsKanbanController=require('mrp.MrpDocumentsKanbanController');
consttestUtils=require('web.test_utils');

constcreateView=testUtils.createView;

QUnit.module('Views',{},function(){

QUnit.module('MrpDocumentsKanbanView',{
    beforeEach:function(){
        this.ORIGINAL_CREATE_XHR=MrpDocumentsKanbanController.prototype._createXHR;
        this.patchDocumentXHR=(mockedXHRs,customSend)=>{
            MrpDocumentsKanbanController.prototype._createXhr=()=>{
                constxhr={
                    upload:newwindow.EventTarget(),
                    open(){},
                    send(data){customSend&&customSend(data);},
                };
                mockedXHRs.push(xhr);
                returnxhr;
            };
        };
        this.data={
            'mrp.document':{
                fields:{
                    name:{string:"Name",type:'char',default:''},
                    priority:{string:'priority',type:'selection',
                        selection:[['0','Normal'],['1','Low'],['2','High'],['3','VeryHigh']]},
                },
                records:[
                    {id:1,name:'test1',priority:2},
                    {id:4,name:'test2',priority:1},
                    {id:3,name:'test3',priority:3},
                ],
            },
        };
    },
    afterEach(){
        MrpDocumentsKanbanController.prototype._createXHR=this.ORIGINAL_CREATE_XHR;
    },
},function(){
    QUnit.test('MRPdocumentskanbanbasicrendering',asyncfunction(assert){
        assert.expect(6);

        constkanban=awaitcreateView({
            View:MrpDocumentsKanbanView,
            model:'mrp.document',
            data:this.data,
            arch:'<kanban><templates><tt-name="kanban-box">'+
                    '<div>'+
                        '<fieldname="name"/>'+
                    '</div>'+
                '</t></templates></kanban>',
        });

        assert.ok(kanban,"kanbaniscreated");
        assert.ok(kanban.$buttons.find('.o_mrp_documents_kanban_upload'),
            "shouldhaveuploadbuttoninkanbanbuttons");
        assert.containsN(kanban,'.o_kanban_view.o_kanban_record:not(.o_kanban_ghost)',3,
            "shouldhave3recordsintherenderer");
        //checkviewlayout
        assert.hasClass(kanban.$('.o_kanban_view'),'o_mrp_documents_kanban_view',
            "shouldhaveclassname'o_mrp_documents_kanban_view'");
        //checkcontrolpanelbuttons
        assert.containsN(kanban,'.o_cp_buttons.btn-primary',1,
            "shouldhaveonly1primarybuttoni.e.Uploadbutton");
        assert.strictEqual(kanban.$('.o_cp_buttons.btn-primary:first').text().trim(),'Upload',
            "shouldhaveaprimary'Upload'button");

        kanban.destroy();
    });

    QUnit.test('mrp:uploadmultiplefiles',asyncfunction(assert){
        assert.expect(4);

        constfile1=awaittestUtils.file.createFile({
            name:'text1.txt',
            content:'hello,world',
            contentType:'text/plain',
        });
        constfile2=awaittestUtils.file.createFile({
            name:'text2.txt',
            content:'hello,world',
            contentType:'text/plain',
        });
        constfile3=awaittestUtils.file.createFile({
            name:'text3.txt',
            content:'hello,world',
            contentType:'text/plain',
        });

        constmockedXHRs=[];
        this.patchDocumentXHR(mockedXHRs,data=>assert.step('xhrSend'));

        constkanban=awaitcreateView({
            View:MrpDocumentsKanbanView,
            model:'mrp.document',
            data:this.data,
            arch:'<kanban><templates><tt-name="kanban-box">'+
                    '<div>'+
                        '<fieldname="name"/>'+
                    '</div>'+
                '</t></templates></kanban>',
        });

        kanban.trigger_up('upload_file',{files:[file1]});
        awaittestUtils.nextTick();
        assert.verifySteps(['xhrSend']);

        kanban.trigger_up('upload_file',{files:[file2,file3]});
        awaittestUtils.nextTick();
        assert.verifySteps(['xhrSend']);

        kanban.destroy();
    });

    QUnit.test('mrp:uploadprogressbars',asyncfunction(assert){
        assert.expect(4);

        constfile1=awaittestUtils.file.createFile({
            name:'text1.txt',
            content:'hello,world',
            contentType:'text/plain',
        });

        constmockedXHRs=[];
        this.patchDocumentXHR(mockedXHRs,data=>assert.step('xhrSend'));

        constkanban=awaitcreateView({
            View:MrpDocumentsKanbanView,
            model:'mrp.document',
            data:this.data,
            arch:'<kanban><templates><tt-name="kanban-box">'+
                    '<div>'+
                        '<fieldname="name"/>'+
                    '</div>'+
                '</t></templates></kanban>',
        });

        kanban.trigger_up('upload_file',{files:[file1]});
        awaittestUtils.nextTick();
        assert.verifySteps(['xhrSend']);

        constprogressEvent=newEvent('progress',{bubbles:true});
        progressEvent.loaded=250000000;
        progressEvent.total=500000000;
        progressEvent.lengthComputable=true;
        mockedXHRs[0].upload.dispatchEvent(progressEvent);
        assert.strictEqual(
            kanban.$('.o_file_upload_progress_text_left').text(),
            "Uploading...(50%)",
            "thecurrentuploadprogressshouldbeat50%"
        );

        progressEvent.loaded=350000000;
        mockedXHRs[0].upload.dispatchEvent(progressEvent);
        assert.strictEqual(
            kanban.$('.o_file_upload_progress_text_right').text(),
            "(350/500Mb)",
            "thecurrentuploadprogressshouldbeat(350/500Mb)"
        );

        kanban.destroy();
    });
});

});

});
