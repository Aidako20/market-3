flectra.define('mail.document_viewer_tests',function(require){
"usestrict";

varDocumentViewer=require('mail.DocumentViewer');

vartestUtils=require('web.test_utils');
varWidget=require('web.Widget');

/**
 *@param{Object}params
 *@param{Object[]}params.attachments
 *@param{int}params.attachmentID
 *@param{function}[params.mockRPC]
 *@param{boolean}[params.debug]
 *@returns{DocumentViewer}
 */
varcreateViewer=asyncfunction(params){
    varparent=newWidget();
    varviewer=newDocumentViewer(parent,params.attachments,params.attachmentID);

    varmockRPC=function(route){
        if(route==='/web/static/lib/pdfjs/web/viewer.html?file=/web/content/1?model%3Dir.attachment%26filename%3DfilePdf.pdf'){
            returnPromise.resolve();
        }
        if(route==='https://www.youtube.com/embed/FYqW0Gdwbzk'){
            returnPromise.resolve();
        }
        if(route==='/web/content/4?model=ir.attachment'){
            returnPromise.resolve();
        }
        if(route==='/web/image/6?unique=56789abc&model=ir.attachment'){
            returnPromise.resolve();
        }
    };
    awaittestUtils.mock.addMockEnvironment(parent,{
        mockRPC:function(){
            if(params.mockRPC){
                var_super=this._super;
                this._super=mockRPC;
                vardef=params.mockRPC.apply(this,arguments);
                this._super=_super;
                returndef;
            }else{
                returnmockRPC.apply(this,arguments);
            }
        },
        intercepts:params.intercepts||{},
    });
    var$target=$("#qunit-fixture");
    if(params.debug){
        $target=$('body');
        $target.addClass('debug');
    }

    //actuallydestroytheparentwhentheviewerisdestroyed
    viewer.destroy=function(){
        deleteviewer.destroy;
        parent.destroy();
    };
    returnviewer.appendTo($target).then(function(){
        returnviewer;
    });
};

QUnit.module('mail',{},function(){
QUnit.module('document_viewer_tests.js',{
    beforeEach:function(){
        this.attachments=[
            {id:1,name:'filePdf.pdf',type:'binary',mimetype:'application/pdf',datas:'R0lGOP////ywAADs='},
            {id:2,name:'urlYoutube',type:'url',mimetype:'',url:'https://youtu.be/FYqW0Gdwbzk'},
            {id:3,name:'urlRandom',type:'url',mimetype:'',url:'https://www.google.com'},
            {id:4,name:'text.html',type:'binary',mimetype:'text/html',datas:'testee'},
            {id:5,name:'video.mp4',type:'binary',mimetype:'video/mp4',datas:'R0lDOP////ywAADs='},
            {id:6,name:'image.jpg',type:'binary',mimetype:'image/jpeg',checksum:'123456789abc',datas:'R0lVOP////ywAADs='},
        ];
    },
},function(){

    QUnit.test('basicrendering',asyncfunction(assert){
        assert.expect(7);

        varviewer=awaitcreateViewer({
            attachmentID:1,
            attachments:this.attachments,
        });

        assert.containsOnce(viewer,'.o_viewer_content',
            "thereshouldbeapreview");
        assert.containsOnce(viewer,'.o_close_btn',
            "thereshouldbeaclosebutton");
        assert.containsOnce(viewer,'.o_viewer-header',
            "thereshouldbeaheader");
        assert.containsOnce(viewer,'.o_image_caption',
            "thereshouldbeanimagecaption");
        assert.containsOnce(viewer,'.o_viewer_zoomer',
            "thereshouldbeazoomer");
        assert.containsOnce(viewer,'.fa-chevron-right',
            "thereshouldbearightnavicon");
        assert.containsOnce(viewer,'.fa-chevron-left',
            "thereshouldbealeftnavicon");

        viewer.destroy();
    });

    QUnit.test('DocumentViewerYoutube',asyncfunction(assert){
        assert.expect(3);

        varyoutubeURL='https://www.youtube.com/embed/FYqW0Gdwbzk';
        varviewer=awaitcreateViewer({
            attachmentID:2,
            attachments:this.attachments,
            mockRPC:function(route){
                if(route===youtubeURL){
                    assert.ok(true,"shouldhavecalledyoutubeURL");
                }
                returnthis._super.apply(this,arguments);
            },
        });

        assert.strictEqual(viewer.$(".o_image_caption:contains('urlYoutube')").length,1,
            "theviewershouldbeontherightattachment");
        assert.containsOnce(viewer,'.o_viewer_text[data-src="'+youtubeURL+'"]',
            "thereshouldbeavideoplayer");

        viewer.destroy();
    });

    QUnit.test('DocumentViewerhtml/(txt)',asyncfunction(assert){
        assert.expect(2);

        varviewer=awaitcreateViewer({
            attachmentID:4,
            attachments:this.attachments,
        });

        assert.strictEqual(viewer.$(".o_image_caption:contains('text.html')").length,1,
            "theviewerbeontherightattachment");
        assert.containsOnce(viewer,'iframe[data-src="/web/content/4?model=ir.attachment"]',
            "thereshouldbeaniframewiththerightsrc");

        viewer.destroy();
    });

    QUnit.test('DocumentViewermp4',asyncfunction(assert){
        assert.expect(2);

        varviewer=awaitcreateViewer({
            attachmentID:5,
            attachments:this.attachments,
        });

        assert.strictEqual(viewer.$(".o_image_caption:contains('video.mp4')").length,1,
            "theviewerbeontherightattachment");
        assert.containsOnce(viewer,'.o_viewer_video',
            "thereshouldbeavideoplayer");

        viewer.destroy();
    });

    QUnit.test('DocumentViewerjpg',asyncfunction(assert){
        assert.expect(2);

        varviewer=awaitcreateViewer({
            attachmentID:6,
            attachments:this.attachments,
        });

        assert.strictEqual(viewer.$(".o_image_caption:contains('image.jpg')").length,1,
            "theviewerbeontherightattachment");
        assert.containsOnce(viewer,'img[data-src="/web/image/6?unique=56789abc&model=ir.attachment"]',
            "thereshouldbeavideoplayer");

        viewer.destroy();
    });

    QUnit.test('isclosablebybutton',asyncfunction(assert){
        assert.expect(3);

        varviewer=awaitcreateViewer({
            attachmentID:6,
            attachments:this.attachments,
        });

        assert.containsOnce(viewer,'.o_viewer_content',
            "shouldhaveadocumentviewer");
        assert.containsOnce(viewer,'.o_close_btn',
            "shouldhaveaclosebutton");

        awaittestUtils.dom.click(viewer.$('.o_close_btn'));

        assert.ok(viewer.isDestroyed(),'viewershouldbedestroyed');
    });

    QUnit.test('isclosablebyclickingonthewrapper',asyncfunction(assert){
        assert.expect(3);

        varviewer=awaitcreateViewer({
            attachmentID:6,
            attachments:this.attachments,
        });

        assert.containsOnce(viewer,'.o_viewer_content',
            "shouldhaveadocumentviewer");
        assert.containsOnce(viewer,'.o_viewer_img_wrapper',
            "shouldhaveawrapper");

        awaittestUtils.dom.click(viewer.$('.o_viewer_img_wrapper'));

        assert.ok(viewer.isDestroyed(),'viewershouldbedestroyed');
    });

    QUnit.test('fileTypeandintegritytest',asyncfunction(assert){
        assert.expect(3);

        varviewer=awaitcreateViewer({
            attachmentID:2,
            attachments:this.attachments,
        });

        assert.strictEqual(this.attachments[1].type,'url',
            "thetypeshouldbeurl");
        assert.strictEqual(this.attachments[1].fileType,'youtu',
            "thereshouldbeafileType'youtu'");
        assert.strictEqual(this.attachments[1].youtube,'FYqW0Gdwbzk',
            "thereshouldbeayoutubetoken");

        viewer.destroy();
    });
});
});

});
