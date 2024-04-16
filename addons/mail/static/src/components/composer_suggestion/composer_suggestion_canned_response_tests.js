flectra.define('mail/static/src/components/composer_suggestion/composer_suggestion_canned_response_tests.js',function(require){
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
QUnit.module('composer_suggestion_canned_response_tests.js',{
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

QUnit.test('cannedresponsesuggestiondisplayed',asyncfunction(assert){
    assert.expect(1);

    this.data['mail.channel'].records.push({id:20});
    awaitthis.start();
    constthread=this.env.models['mail.thread'].findFromIdentifyingData({
        id:20,
        model:'mail.channel',
    });
    constcannedResponse=this.env.models['mail.canned_response'].create({
        id:7,
        source:'hello',
        substitution:"Hello,howareyou?",
    });
    awaitthis.createComposerSuggestion({
        composerLocalId:thread.composer.localId,
        isActive:true,
        modelName:'mail.canned_response',
        recordLocalId:cannedResponse.localId,
    });

    assert.containsOnce(
        document.body,
        `.o_ComposerSuggestion`,
        "Cannedresponsesuggestionshouldbepresent"
    );
});

QUnit.test('cannedresponsesuggestioncorrectdata',asyncfunction(assert){
    assert.expect(5);

    this.data['mail.channel'].records.push({id:20});
    awaitthis.start();
    constthread=this.env.models['mail.thread'].findFromIdentifyingData({
        id:20,
        model:'mail.channel',
    });
    constcannedResponse=this.env.models['mail.canned_response'].create({
        id:7,
        source:'hello',
        substitution:"Hello,howareyou?",
    });
    awaitthis.createComposerSuggestion({
        composerLocalId:thread.composer.localId,
        isActive:true,
        modelName:'mail.canned_response',
        recordLocalId:cannedResponse.localId,
    });

    assert.containsOnce(
        document.body,
        '.o_ComposerSuggestion',
        "Cannedresponsesuggestionshouldbepresent"
    );
    assert.containsOnce(
        document.body,
        '.o_ComposerSuggestion_part1',
        "Cannedresponsesourceshouldbepresent"
    );
    assert.strictEqual(
        document.querySelector(`.o_ComposerSuggestion_part1`).textContent,
        "hello",
        "Cannedresponsesourceshouldbedisplayed"
    );
    assert.containsOnce(
        document.body,
        '.o_ComposerSuggestion_part2',
        "Cannedresponsesubstitutionshouldbepresent"
    );
    assert.strictEqual(
        document.querySelector(`.o_ComposerSuggestion_part2`).textContent,
        "Hello,howareyou?",
        "Cannedresponsesubstitutionshouldbedisplayed"
    );
});

QUnit.test('cannedresponsesuggestionactive',asyncfunction(assert){
    assert.expect(2);

    this.data['mail.channel'].records.push({id:20});
    awaitthis.start();
    constthread=this.env.models['mail.thread'].findFromIdentifyingData({
        id:20,
        model:'mail.channel',
    });
    constcannedResponse=this.env.models['mail.canned_response'].create({
        id:7,
        source:'hello',
        substitution:"Hello,howareyou?",
    });
    awaitthis.createComposerSuggestion({
        composerLocalId:thread.composer.localId,
        isActive:true,
        modelName:'mail.canned_response',
        recordLocalId:cannedResponse.localId,
    });

    assert.containsOnce(
        document.body,
        '.o_ComposerSuggestion',
        "Cannedresponsesuggestionshouldbedisplayed"
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
