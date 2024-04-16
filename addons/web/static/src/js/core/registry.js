flectra.define("web.Registry",function(require){
    "usestrict";

    const{sortBy}=require("web.utils");

    /**
     *Theregistryisreallyprettymuchonlyamappingfromsomekeystosome
     *values.TheRegistryclassonlyaddafewsimplemethodsaroundthattomake
     *itnicerandslightlysafer.
     *
     *Notethatregistrieshaveafundamentalproblem:thevaluethatyoutryto
     *getinaregistrymightnothavebeenaddedyet,soofcourse,youneedto
     *makesurethatyourdependenciesaresolid. Forthisreason,itisagood
     *practicetoavoidusingtheregistryifyoucansimplyimportwhatyouneed
     *withthe'require'statement.
     *
     *However,ontheflipside,sometimesyoucannotjustsimplyimportsomething
     *becausewewouldhaveadependencycycle. Inthatcase,registriesmight
     *help.
     */
    classRegistry{
        /**
         *@functionpredicate
         *@param{any}value
         *@returns{boolean}
         */
        /**
         *@param{Object}[mapping]theinitialdataintheregistry
         *@param{predicate}[predicate=(()=>true)]predicatethateach
         *     addedvaluemustpasstoberegistered.
         */
        constructor(mapping,predicate=()=>true){
            this.map=Object.create(mapping||null);
            this._scoreMapping=Object.create(null);
            this._sortedKeys=null;
            this.listeners=[];//listeningcallbacksonnewlyaddeditems.
            this.predicate=predicate;
        }

        //--------------------------------------------------------------------------
        //Public
        //--------------------------------------------------------------------------

        /**
         *Addakey(andavalue)totheregistry.
         *Notifythelistenersonnewlyaddeditemintheregistry.
         *@param{string}key
         *@param{any}value
         *@param{number}[score]ifgiven,thisvaluewillbeusedtoorderkeys
         *@returns{Registry}canbeusedtochainaddcalls.
         */
        add(key,value,score){
            if(!this.predicate(value)){
                thrownewError(`Valueofkey"${key}"doesnotpasstheadditionpredicate.`);
            }
            this._scoreMapping[key]=score===undefined?key:score;
            this._sortedKeys=null;
            this.map[key]=value;
            for(constcallbackofthis.listeners){
                callback(key,value);
            }
            returnthis;
        }

        /**
         *Checkiftheregistrycontainsthekey
         *@param{string}key
         *@returns{boolean}
         */
        contains(key){
            returnkeyinthis.map;
        }

        /**
         *Returnsthecontentoftheregistry(anobjectmappingkeystovalues)
         *@returns{Object}
         */
        entries(){
            constentries={};
            constkeys=this.keys();
            for(constkeyofkeys){
                entries[key]=this.map[key];
            }
            returnentries;
        }

        /**
         *Returnsthevalueassociatedtothegivenkey.
         *@param{string}key
         *@returns{any}
         */
        get(key){
            returnthis.map[key];
        }

        /**
         *Triesanumberofkeys,andreturnsthefirstobjectmatchingoneof
         *thekeys.
         *@param{string[]}keysasequenceofkeystofetchtheobjectfor
         *@returns{any}thefirstresultfoundmatchinganobject
         */
        getAny(keys){
            for(constkeyofkeys){
                if(keyinthis.map){
                    returnthis.map[key];
                }
            }
            returnnull;
        }

        /**
         *Returnthelistofkeysinmapobject.
         *
         *Theregistryguaranteesthatthekeyshaveaconsistentorder,definedby
         *the'score'valuewhentheitemhasbeenadded.
         *@returns{string[]}
         */
        keys(){
            if(!this._sortedKeys){
                constkeys=[];
                for(constkeyinthis.map){
                    keys.push(key);
                }
                this._sortedKeys=sortBy(keys,
                    key=>this._scoreMapping[key]||0
                );
            }
            returnthis._sortedKeys;
        }

        /**
         *@functiononAddCallback
         *@param{string}key
         *@param{any}value
         */
        /**
         *Registeracallbacktoexecutewhenitemsareaddedtotheregistry.
         *@param{onAddCallback}callbackfunctionwithparameters(key,value).
         */
        onAdd(callback){
            this.listeners.push(callback);
        }

        /**
         *Returnthelistofvaluesinmapobject
         *@returns{string[]}
         */
        values(){
            returnthis.keys().map((key)=>this.map[key]);
        }
    }

    returnRegistry;
});
