flectra.define('mail/static/src/components/composer_suggestion/composer_suggestion.js',function(require){
'usestrict';

constuseShouldUpdateBasedOnProps=require('mail/static/src/component_hooks/use_should_update_based_on_props/use_should_update_based_on_props.js');
constuseStore=require('mail/static/src/component_hooks/use_store/use_store.js');
constuseUpdate=require('mail/static/src/component_hooks/use_update/use_update.js');

constcomponents={
    PartnerImStatusIcon:require('mail/static/src/components/partner_im_status_icon/partner_im_status_icon.js'),
};

const{Component}=owl;

classComposerSuggestionextendsComponent{

    /**
     *@override
     */
    constructor(...args){
        super(...args);
        useShouldUpdateBasedOnProps();
        useStore(props=>{
            constcomposer=this.env.models['mail.composer'].get(this.props.composerLocalId);
            constrecord=this.env.models[props.modelName].get(props.recordLocalId);
            return{
                composerHasToScrollToActiveSuggestion:composer&&composer.hasToScrollToActiveSuggestion,
                record:record?record.__state:undefined,
            };
        });
        useUpdate({func:()=>this._update()});
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

    getisCannedResponse(){
        returnthis.props.modelName==="mail.canned_response";
    }

    getisChannel(){
        returnthis.props.modelName==="mail.thread";
    }

    getisCommand(){
        returnthis.props.modelName==="mail.channel_command";
    }

    getisPartner(){
        returnthis.props.modelName==="mail.partner";
    }

    getrecord(){
        returnthis.env.models[this.props.modelName].get(this.props.recordLocalId);
    }

    /**
     *Returnsadescriptivetitleforthissuggestion.Usefultobeableto
     *readbothpartswhentheyareoverflowingtheUI.
     *
     *@returns{string}
     */
    title(){
        if(this.isCannedResponse){
            return_.str.sprintf("%s:%s",this.record.source,this.record.substitution);
        }
        if(this.isChannel){
            returnthis.record.name;
        }
        if(this.isCommand){
            return_.str.sprintf("%s:%s",this.record.name,this.record.help);
        }
        if(this.isPartner){
            if(this.record.email){
                return_.str.sprintf("%s(%s)",this.record.nameOrDisplayName,this.record.email);
            }
            returnthis.record.nameOrDisplayName;
        }
        return"";
    }

    //--------------------------------------------------------------------------
    //Private
    //--------------------------------------------------------------------------

    /**
     *@private
     */
    _update(){
        if(
            this.composer&&
            this.composer.hasToScrollToActiveSuggestion&&
            this.props.isActive
        ){
            this.el.scrollIntoView({
                block:'center',
            });
            this.composer.update({hasToScrollToActiveSuggestion:false});
        }
    }

    //--------------------------------------------------------------------------
    //Handlers
    //--------------------------------------------------------------------------

    /**
     *@private
     *@param{Event}ev
     */
    _onClick(ev){
        ev.preventDefault();
        this.composer.update({activeSuggestedRecord:[['link',this.record]]});
        this.composer.insertSuggestion();
        this.composer.closeSuggestions();
        this.trigger('o-composer-suggestion-clicked');
    }

}

Object.assign(ComposerSuggestion,{
    components,
    defaultProps:{
        isActive:false,
    },
    props:{
        composerLocalId:String,
        isActive:Boolean,
        modelName:String,
        recordLocalId:String,
    },
    template:'mail.ComposerSuggestion',
});

returnComposerSuggestion;

});
