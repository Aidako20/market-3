flectra.define('mail/static/src/components/file_uploader/file_uploader_tests.js',function(require){
"usestrict";

constcomponents={
    FileUploader:require('mail/static/src/components/file_uploader/file_uploader.js'),
};
const{
    afterEach,
    beforeEach,
    createRootComponent,
    nextAnimationFrame,
    start,
}=require('mail/static/src/utils/test_utils.js');

const{
    file:{
        createFile,
        inputFiles,
    },
}=require('web.test_utils');

QUnit.module('mail',{},function(){
QUnit.module('components',{},function(){
QUnit.module('file_uploader',{},function(){
QUnit.module('file_uploader_tests.js',{
    beforeEach(){
        beforeEach(this);
        this.components=[];

        this.createFileUploaderComponent=asyncotherProps=>{
            constprops=Object.assign({attachmentLocalIds:[]},otherProps);
            returncreateRootComponent(this,components.FileUploader,{
                props,
                target:this.widget.el,
            });
        };

        this.start=asyncparams=>{
            const{env,widget}=awaitstart(Object.assign({},params,{
                data:this.data,
            }));
            this.env=env;
            this.widget=widget;
        };
    },
    afterEach(){
        afterEach(this);
    },
});

QUnit.test('noconflictsbetweenfileuploaders',asyncfunction(assert){
    assert.expect(2);

    awaitthis.start();
    constfileUploader1=awaitthis.createFileUploaderComponent();
    constfileUploader2=awaitthis.createFileUploaderComponent();
    constfile1=awaitcreateFile({
        name:'text1.txt',
        content:'hello,world',
        contentType:'text/plain',
    });
    inputFiles(
        fileUploader1.el.querySelector('.o_FileUploader_input'),
        [file1]
    );
    awaitnextAnimationFrame();//wecan'tuseafterNextRenderasfileInputaredisplay:none
    assert.strictEqual(
        this.env.models['mail.attachment'].all().length,
        1,
        'Uploadedfileshouldbetheonlyattachmentcreated'
    );

    constfile2=awaitcreateFile({
        name:'text2.txt',
        content:'hello,world',
        contentType:'text/plain',
    });
    inputFiles(
        fileUploader2.el.querySelector('.o_FileUploader_input'),
        [file2]
    );
    awaitnextAnimationFrame();
    assert.strictEqual(
        this.env.models['mail.attachment'].all().length,
        2,
        'Uploadedfileshouldbetheonlyattachmentadded'
    );
});

});
});
});

});
