flectra.define('mail/static/src/models/channel_command/channel_command.js',function(require){
'usestrict';

const{registerNewModel}=require('mail/static/src/model/model_core.js');
const{attr}=require('mail/static/src/model/model_field.js');
const{cleanSearchTerm}=require('mail/static/src/utils/utils.js');

functionfactory(dependencies){

    classChannelCommandextendsdependencies['mail.model']{

        /**
         *Fetcheschannelcommandsmatchingthegivensearchtermtoextendthe
         *JSknowledgeandtoupdatethesuggestionlistaccordingly.
         *
         *Inpracticeallchannelcommandsarealreadyfetchedatinitsothis
         *methoddoesnothing.
         *
         *@static
         *@param{string}searchTerm
         *@param{Object}[options={}]
         *@param{mail.thread}[options.thread]prioritizeand/orrestrict
         * resultinthecontextofgiventhread
         */
        staticfetchSuggestions(searchTerm,{thread}={}){}

        /**
         *Returnsasortfunctiontodeterminetheorderofdisplayofchannel
         *commandsinthesuggestionlist.
         *
         *@static
         *@param{string}searchTerm
         *@param{Object}[options={}]
         *@param{mail.thread}[options.thread]prioritizeresultinthe
         * contextofgiventhread
         *@returns{function}
         */
        staticgetSuggestionSortFunction(searchTerm,{thread}={}){
            constcleanedSearchTerm=cleanSearchTerm(searchTerm);
            return(a,b)=>{
                constisATypeSpecific=a.channel_types;
                constisBTypeSpecific=b.channel_types;
                if(isATypeSpecific&&!isBTypeSpecific){
                    return-1;
                }
                if(!isATypeSpecific&&isBTypeSpecific){
                    return1;
                }
                constcleanedAName=cleanSearchTerm(a.name||'');
                constcleanedBName=cleanSearchTerm(b.name||'');
                if(cleanedAName.startsWith(cleanedSearchTerm)&&!cleanedBName.startsWith(cleanedSearchTerm)){
                    return-1;
                }
                if(!cleanedAName.startsWith(cleanedSearchTerm)&&cleanedBName.startsWith(cleanedSearchTerm)){
                    return1;
                }
                if(cleanedAName<cleanedBName){
                    return-1;
                }
                if(cleanedAName>cleanedBName){
                    return1;
                }
                returna.id-b.id;
            };
        }

        /**
         *Returnschannelcommandsthatmatchthegivensearchterm.
         *
         *@static
         *@param{string}searchTerm
         *@param{Object}[options={}]
         *@param{mail.thread}[options.thread]prioritizeand/orrestrict
         * resultinthecontextofgiventhread
         *@returns{[mail.channel_command[],mail.channel_command[]]}
         */
        staticsearchSuggestions(searchTerm,{thread}={}){
            if(thread.model!=='mail.channel'){
                //channelcommandsarechannelspecific
                return[[]];
            }
            constcleanedSearchTerm=cleanSearchTerm(searchTerm);
            return[this.env.messaging.commands.filter(command=>{
                if(!cleanSearchTerm(command.name).includes(cleanedSearchTerm)){
                    returnfalse;
                }
                if(command.channel_types){
                    returncommand.channel_types.includes(thread.channel_type);
                }
                returntrue;
            })];
        }

        /**
         *Returnsthetextthatidentifiesthischannelcommandinamention.
         *
         *@returns{string}
         */
        getMentionText(){
            returnthis.name;
        }

    }

    ChannelCommand.fields={
        /**
         *Determinesonwhichchanneltypes`this`isavailable.
         *Typeofthechannel(e.g.'chat','channel'or'groups')
         *Thisfieldshouldcontainanarraywhenfilteringisdesired.
         *Otherwise,itshouldbeundefinedwhenalltypesareallowed.
         */
        channel_types:attr(),
        /**
         * Thecommandthatwillbeexecuted.
         */
        help:attr(),
        /**
         * Thekeywordtouseaspecificcommand.
         */
        name:attr(),
    };

    ChannelCommand.modelName='mail.channel_command';

    returnChannelCommand;
}

registerNewModel('mail.channel_command',factory);

});
