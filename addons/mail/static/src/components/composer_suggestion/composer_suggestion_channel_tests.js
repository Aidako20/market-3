flectra.define('mail/static/src/components/composer_suggestion/composer_suggestion_channel_tests.js',function(require){
'usestrict';

constcomponents={
    ComposerSuggestion:require('mail/static/src/components/composer_suggestion/composer_suggestion.js'),
};
const{
    afterEach,
    beforeEach,
    createRootComponent,
    start,
}=require('mail/static/src/utils/test_utils.js');

QUnit.module('mail',{},function(){
QUnit.module('components',{},function(){
QUnit.module('composer_suggestion',{},function(){
QUnit.module('composer_suggestion_channel_tests.js',{
    beforeEach(){
        beforeEach(this);

        this.createComposerSuggestion=asyncprops=>{
            awaitcreateRootComponent(this,components.ComposerSuggestion,{
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

QUnit.test('channelmentionsuggestiondisplayed',asyncfunction(assert){
    assert.expect(1);

    this.data['mail.channel'].records.push({id:20});
    awaitthis.start();
    constthread=this.env.models['mail.thread'].findFromIdentifyingData({
        id:20,
        model:'mail.channel',
    });
    constchannel=this.env.models['mail.thread'].create({
        id:7,
        name:"General",
        model:'mail.channel',
    });
    awaitthis.createComposerSuggestion({
        composerLocalId:thread.composer.localId,
        isActive:true,
        modelName:'mail.thread',
        recordLocalId:channel.localId,
    });

    assert.containsOnce(
        document.body,
        `.o_ComposerSuggestion`,
        "Channelmentionsuggestionshouldbepresent"
    );
});

QUnit.test('channelmentionsuggestioncorrectdata',asyncfunction(assert){
    assert.expect(3);

    this.data['mail.channel'].records.push({id:20});
    awaitthis.start();
    constthread=this.env.models['mail.thread'].findFromIdentifyingData({
        id:20,
        model:'mail.channel',
    });
    constchannel=this.env.models['mail.thread'].create({
        id:7,
        name:"General",
        model:'mail.channel',
    });
    awaitthis.createComposerSuggestion({
        composerLocalId:thread.composer.localId,
        isActive:true,
        modelName:'mail.thread',
        recordLocalId:channel.localId,
    });

    assert.containsOnce(
        document.body,
        '.o_ComposerSuggestion',
        "Channelmentionsuggestionshouldbepresent"
    );
    assert.containsOnce(
        document.body,
        '.o_ComposerSuggestion_part1',
        "Channelnameshouldbepresent"
    );
    assert.strictEqual(
        document.querySelector(`.o_ComposerSuggestion_part1`).textContent,
        "General",
        "Channelnameshouldbedisplayed"
    );
});

QUnit.test('channelmentionsuggestionactive',asyncfunction(assert){
    assert.expect(2);

    this.data['mail.channel'].records.push({id:20});
    awaitthis.start();
    constthread=this.env.models['mail.thread'].findFromIdentifyingData({
        id:20,
        model:'mail.channel',
    });
    constchannel=this.env.models['mail.thread'].create({
        id:7,
        name:"General",
        model:'mail.channel',
    });
    awaitthis.createComposerSuggestion({
        composerLocalId:thread.composer.localId,
        isActive:true,
        modelName:'mail.thread',
        recordLocalId:channel.localId,
    });

    assert.containsOnce(
        document.body,
        '.o_ComposerSuggestion',
        "Channelmentionsuggestionshouldbedisplayed"
    );
    assert.hasClass(
        document.querySelector('.o_ComposerSuggestion'),
        'active',
        "shouldbeactiveinitially"
    );
});

});
});
});

});
