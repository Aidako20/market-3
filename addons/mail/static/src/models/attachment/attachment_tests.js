flectra.define('mail/static/src/models/attachment/attachment_tests.js',function(require){
'usestrict';

const{afterEach,beforeEach,start}=require('mail/static/src/utils/test_utils.js');

QUnit.module('mail',{},function(){
QUnit.module('models',{},function(){
QUnit.module('attachment',{},function(){
QUnit.module('attachment_tests.js',{
    beforeEach(){
        beforeEach(this);

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

QUnit.test('create(txt)',asyncfunction(assert){
    assert.expect(9);

    awaitthis.start();
    assert.notOk(this.env.models['mail.attachment'].findFromIdentifyingData({id:750}));

    constattachment=this.env.models['mail.attachment'].create({
        filename:"test.txt",
        id:750,
        mimetype:'text/plain',
        name:"test.txt",
    });
    assert.ok(attachment);
    assert.ok(this.env.models['mail.attachment'].findFromIdentifyingData({id:750}));
    assert.strictEqual(this.env.models['mail.attachment'].findFromIdentifyingData({id:750}),attachment);
    assert.strictEqual(attachment.filename,"test.txt");
    assert.strictEqual(attachment.id,750);
    assert.notOk(attachment.isTemporary);
    assert.strictEqual(attachment.mimetype,'text/plain');
    assert.strictEqual(attachment.name,"test.txt");
});

QUnit.test('displayName',asyncfunction(assert){
    assert.expect(5);

    awaitthis.start();
    assert.notOk(this.env.models['mail.attachment'].findFromIdentifyingData({id:750}));

    constattachment=this.env.models['mail.attachment'].create({
        filename:"test.txt",
        id:750,
        mimetype:'text/plain',
        name:"test.txt",
    });
    assert.ok(attachment);
    assert.ok(this.env.models['mail.attachment'].findFromIdentifyingData({id:750}));
    assert.strictEqual(attachment,this.env.models['mail.attachment'].findFromIdentifyingData({id:750}));
    assert.strictEqual(attachment.displayName,"test.txt");
});

QUnit.test('extension',asyncfunction(assert){
    assert.expect(5);

    awaitthis.start();
    assert.notOk(this.env.models['mail.attachment'].findFromIdentifyingData({id:750}));

    constattachment=this.env.models['mail.attachment'].create({
        filename:"test.txt",
        id:750,
        mimetype:'text/plain',
        name:"test.txt",
    });
    assert.ok(attachment);
    assert.ok(this.env.models['mail.attachment'].findFromIdentifyingData({id:750}));
    assert.strictEqual(attachment,this.env.models['mail.attachment'].findFromIdentifyingData({id:750}));
    assert.strictEqual(attachment.extension,'txt');
});

QUnit.test('fileType',asyncfunction(assert){
    assert.expect(5);

    awaitthis.start();
    assert.notOk(this.env.models['mail.attachment'].findFromIdentifyingData({id:750}));

    constattachment=this.env.models['mail.attachment'].create({
        filename:"test.txt",
        id:750,
        mimetype:'text/plain',
        name:"test.txt",
    });
    assert.ok(attachment);
    assert.ok(this.env.models['mail.attachment'].findFromIdentifyingData({id:750}));
    assert.strictEqual(attachment,this.env.models['mail.attachment'].findFromIdentifyingData({
        id:750,
    }));
    assert.strictEqual(attachment.fileType,'text');
});

QUnit.test('isTextFile',asyncfunction(assert){
    assert.expect(5);

    awaitthis.start();
    assert.notOk(this.env.models['mail.attachment'].findFromIdentifyingData({id:750}));

    constattachment=this.env.models['mail.attachment'].create({
        filename:"test.txt",
        id:750,
        mimetype:'text/plain',
        name:"test.txt",
    });
    assert.ok(attachment);
    assert.ok(this.env.models['mail.attachment'].findFromIdentifyingData({id:750}));
    assert.strictEqual(attachment,this.env.models['mail.attachment'].findFromIdentifyingData({id:750}));
    assert.ok(attachment.isTextFile);
});

QUnit.test('isViewable',asyncfunction(assert){
    assert.expect(5);

    awaitthis.start();
    assert.notOk(this.env.models['mail.attachment'].findFromIdentifyingData({id:750}));

    constattachment=this.env.models['mail.attachment'].create({
        filename:"test.txt",
        id:750,
        mimetype:'text/plain',
        name:"test.txt",
    });
    assert.ok(attachment);
    assert.ok(this.env.models['mail.attachment'].findFromIdentifyingData({id:750}));
    assert.strictEqual(attachment,this.env.models['mail.attachment'].findFromIdentifyingData({id:750}));
    assert.ok(attachment.isViewable);
});

});
});
});

});
