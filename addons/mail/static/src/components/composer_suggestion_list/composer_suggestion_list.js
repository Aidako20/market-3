flectra.define('mail/static/src/components/composer_suggestion_list/composer_suggestion_list.js',function(require){
'usestrict';

constcomponents={
    ComposerSuggestion:require('mail/static/src/components/composer_suggestion/composer_suggestion.js'),
};
constuseShouldUpdateBasedOnProps=require('mail/static/src/component_hooks/use_should_update_based_on_props/use_should_update_based_on_props.js');
constuseStore=require('mail/static/src/component_hooks/use_store/use_store.js');

const{Component}=owl;

classComposerSuggestionListextendsComponent{

    /**
     *@override
     */
    constructor(...args){
        super(...args);
        useShouldUpdateBasedOnProps();
        useStore(props=>{
            constcomposer=this.env.models['mail.composer'].get(props.composerLocalId);
            constactiveSuggestedRecord=composer
                ?composer.activeSuggestedRecord
                :undefined;
            constextraSuggestedRecords=composer
                ?composer.extraSuggestedRecords
                :[];
            constmainSuggestedRecords=composer
                ?composer.mainSuggestedRecords
                :[];
            return{
                activeSuggestedRecord,
                composer,
                composerSuggestionModelName:composer&&composer.suggestionModelName,
                extraSuggestedRecords,
                mainSuggestedRecords,
            };
        },{
            compareDepth:{
                extraSuggestedRecords:1,
                mainSuggestedRecords:1,
            },
        });
    }

    //--------------------------------------------------------------------------
    //Public
    //--------------------------------------------------------------------------

    /**
     *@returns{mail.composer}
     */
    getcomposer(){
        returnthis.env.models['mail.composer'].get(this.props.composerLocalId);
    }

}

Object.assign(ComposerSuggestionList,{
    components,
    defaultProps:{
        isBelow:false,
    },
    props:{
        composerLocalId:String,
        isBelow:Boolean,
    },
    template:'mail.ComposerSuggestionList',
});

returnComposerSuggestionList;

});
