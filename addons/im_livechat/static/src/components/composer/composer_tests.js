flectra.define('im_livechat/static/src/components/composer/composer_tests.js',function(require){
'usestrict';

constcomponents={
    Composer:require('mail/static/src/components/composer/composer.js'),
};
const{
    afterEach,
    afterNextRender,
    beforeEach,
    start,
}=require('mail/static/src/utils/test_utils.js');

QUnit.module('im_livechat',{},function(){
QUnit.module('components',{},function(){
QUnit.module('composer',{},function(){
QUnit.module('composer_tests.js',{
    beforeEach(){
        beforeEach(this);

        this.createComposerComponent=async(composer,otherProps)=>{
            constComposerComponent=components.Composer;
            ComposerComponent.env=this.env;
            this.component=newComposerComponent(null,Object.assign({
                composerLocalId:composer.localId,
            },otherProps));
            deleteComposerComponent.env;
            awaitafterNextRender(()=>this.component.mount(this.widget.el));
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

QUnit.test('livechat:noaddattachmentbutton',asyncfunction(assert){
    //Attachmentsarenotyetsupportedinlivechat,especiallyfromlivechat
    //visitorPoV.Thismaylikelychangeinthefuturewithtask-2029065.
    assert.expect(2);

    awaitthis.start();
    constthread=this.env.models['mail.thread'].create({
        channel_type:'livechat',
        id:10,
        model:'mail.channel',
    });
    awaitthis.createComposerComponent(thread.composer);
    assert.containsOnce(document.body,'.o_Composer',"shouldhaveacomposer");
    assert.containsNone(
        document.body,
        '.o_Composer_buttonAttachment',
        "composerlinkedtolivechatshouldnothavea'Addattachment'button"
    );
});

QUnit.test('livechat:disableattachmentuploadviadraganddrop',asyncfunction(assert){
    assert.expect(2);

    awaitthis.start();
    constthread=this.env.models['mail.thread'].create({
        channel_type:'livechat',
        id:10,
        model:'mail.channel',
    });
    awaitthis.createComposerComponent(thread.composer);
    assert.containsOnce(document.body,'.o_Composer',"shouldhaveacomposer");
    assert.containsNone(
        document.body,
        '.o_Composer_dropZone',
        "composerlinkedtolivechatshouldnothaveadropzone"
    );
});

});
});
});

});
