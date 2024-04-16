flectra.define('mail/static/src/models/canned_response/canned_response.js',function(require){
'usestrict';

const{registerNewModel}=require('mail/static/src/model/model_core.js');
const{attr}=require('mail/static/src/model/model_field.js');
const{cleanSearchTerm}=require('mail/static/src/utils/utils.js');

functionfactory(dependencies){

    classCannedResponseextendsdependencies['mail.model']{

        /**
         *Fetchescannedresponsesmatchingthegivensearchtermtoextendthe
         *JSknowledgeandtoupdatethesuggestionlistaccordingly.
         *
         *Inpracticeallcannedresponsesarealreadyfetchedatinitsothis
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
         *Returnsasortfunctiontodeterminetheorderofdisplayofcanned
         *responsesinthesuggestionlist.
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
                constcleanedAName=cleanSearchTerm(a.source||'');
                constcleanedBName=cleanSearchTerm(b.source||'');
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

        /*
         *Returnscannedresponsesthatmatchthegivensearchterm.
         *
         *@static
         *@param{string}searchTerm
         *@param{Object}[options={}]
         *@param{mail.thread}[options.thread]prioritizeand/orrestrict
         * resultinthecontextofgiventhread
         *@returns{[mail.canned_response[],mail.canned_response[]]}
         */
        staticsearchSuggestions(searchTerm,{thread}={}){
            constcleanedSearchTerm=cleanSearchTerm(searchTerm);
            return[this.env.messaging.cannedResponses.filter(cannedResponse=>
                cleanSearchTerm(cannedResponse.source).includes(cleanedSearchTerm)
            )];
        }

        /**
         *Returnsthetextthatidentifiesthiscannedresponseinamention.
         *
         *@returns{string}
         */
        getMentionText(){
            returnthis.substitution;
        }

    }

    CannedResponse.fields={
        id:attr(),
        /**
         * Thekeywordtouseaspecificcannedresponse.
         */
        source:attr(),
        /**
         *Thecannedresponseitselfwhichwillreplacethekeywordpreviously
         *entered.
         */
        substitution:attr(),
    };

    CannedResponse.modelName='mail.canned_response';

    returnCannedResponse;
}

registerNewModel('mail.canned_response',factory);

});
