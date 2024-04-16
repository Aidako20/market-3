flectra.define('mail/static/src/components/composer_suggestion/composer_suggestion_command_tests.js',function(require){
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
QUnit.module('composer_suggestion_command_tests.js',{
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

QUnit.test('commandsuggestiondisplayed',asyncfunction(assert){
    assert.expect(1);

    this.data['mail.channel'].records.push({id:20});
    awaitthis.start();
    constthread=this.env.models['mail.thread'].findFromIdentifyingData({
        id:20,
        model:'mail.channel',
    });
    constcommand=this.env.models['mail.channel_command'].create({
        name:'whois',
        help:"Displayswhoitis",
    });
    awaitthis.createComposerSuggestion({
        composerLocalId:thread.composer.localId,
        isActive:true,
        modelName:'mail.channel_command',
        recordLocalId:command.localId,
    });

    assert.containsOnce(
        document.body,
        `.o_ComposerSuggestion`,
        "Commandsuggestionshouldbepresent"
    );
});

QUnit.test('commandsuggestioncorrectdata',asyncfunction(assert){
    assert.expect(5);

    this.data['mail.channel'].records.push({id:20});
    awaitthis.start();
    constthread=this.env.models['mail.thread'].findFromIdentifyingData({
        id:20,
        model:'mail.channel',
    });
    constcommand=this.env.models['mail.channel_command'].create({
        name:'whois',
        help:"Displayswhoitis",
    });
    awaitthis.createComposerSuggestion({
        composerLocalId:thread.composer.localId,
        isActive:true,
        modelName:'mail.channel_command',
        recordLocalId:command.localId,
    });

    assert.containsOnce(
        document.body,
        '.o_ComposerSuggestion',
        "Commandsuggestionshouldbepresent"
    );
    assert.containsOnce(
        document.body,
        '.o_ComposerSuggestion_part1',
        "Commandnameshouldbepresent"
    );
    assert.strictEqual(
        document.querySelector(`.o_ComposerSuggestion_part1`).textContent,
        "whois",
        "Commandnameshouldbedisplayed"
    );
    assert.containsOnce(
        document.body,
        '.o_ComposerSuggestion_part2',
        "Commandhelpshouldbepresent"
    );
    assert.strictEqual(
        document.querySelector(`.o_ComposerSuggestion_part2`).textContent,
        "Displayswhoitis",
        "Commandhelpshouldbedisplayed"
    );
});

QUnit.test('commandsuggestionactive',asyncfunction(assert){
    assert.expect(2);

    this.data['mail.channel'].records.push({id:20});
    awaitthis.start();
    constthread=this.env.models['mail.thread'].findFromIdentifyingData({
        id:20,
        model:'mail.channel',
    });
    constcommand=this.env.models['mail.channel_command'].create({
        name:'whois',
        help:"Displayswhoitis",
    });
    awaitthis.createComposerSuggestion({
        composerLocalId:thread.composer.localId,
        isActive:true,
        modelName:'mail.channel_command',
        recordLocalId:command.localId,
    });

    assert.containsOnce(
        document.body,
        '.o_ComposerSuggestion',
        "Commandsuggestionshouldbedisplayed"
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
