flectra.define('mail/static/src/models/Model',function(require){
'usestrict';

const{registerNewModel}=require('mail/static/src/model/model_core.js');
const{RecordDeletedError}=require('mail/static/src/model/model_errors.js');

/**
 *Thisfunctiongeneratesaclassthatrepresentamodel.Instancesofsuch
 *model(orinheritedmodels)representlogicalobjectsusedinwhole
 *application.Theycouldrepresentserverrecord(e.g.Thread,Message)or
 *UIelements(e.g.MessagingMenu,ChatWindow).Theseinstancesarecalled
 *"records",whiletheclassesarecalled"models".
 */
functionfactory(){

    classModel{

        /**
         *@param{Object}[param0={}]
         *@param{boolean}[param0.valid=false]ifset,thisconstructoris
         *  calledbystaticmethod`create()`.Thisshouldalwaysbethecase.
         *@throws{Error}incaseconstructoriscalledinaninvalidway,i.e.
         *  byinstantiatingtherecordmanuallywith`new`insteadoffrom
         *  staticmethod`create()`.
         */
        constructor({valid=false}={}){
            if(!valid){
                thrownewError("Recordmustalwaysbeinstantiatedfromstaticmethod'create()'");
            }
        }

        /**
         *Thisfunctioniscalledduringthecreatecycle,whentherecordhas
         *alreadybeencreated,butitsvalueshavenotyetbeenassigned.
         *
         *Itisusuallypreferabletooverride@see`_created`.
         *
         *Themainusecaseistopreparetherecordfortheassignationofits
         *values,forexampleifacomputedfieldreliesontherecordtohave
         *somepurelytechnicalpropertycorrectlyset.
         *
         *@abstract
         *@private
         */
        _willCreate(){}

        /**
         *Thisfunctioniscalledaftertherecordhasbeencreated,more
         *preciselyattheendoftheupdatecycle(whichmeansallimplicit
         *changessuchascomputeshavebeenappliedtoo).
         *
         *Themainusecaseistoregisterlistenersontherecord.
         *
         *@abstract
         *@private
         */
        _created(){}

        /**
         *Thisfunctioniscalledwhentherecordisabouttobedeleted.The
         *recordstillhasallofitsfieldsvaluesaccessible,butforall
         *intentsandpurposestherecordshouldalreadybeconsidered
         *deleted,whichmeansupdateshouldn'tbecalledinsidethismethod.
         *
         *Themainusecaseistounregisterlistenersontherecord.
         *
         *@abstract
         *@private
         */
        _willDelete(){}

        //----------------------------------------------------------------------
        //Public
        //----------------------------------------------------------------------

        /**
         *Returnsallrecordsofthismodelthatmatchprovidedcriteria.
         *
         *@static
         *@param{function}[filterFunc]
         *@returns{mail.model[]}
         */
        staticall(filterFunc){
            returnthis.env.modelManager.all(this,filterFunc);
        }

        /**
         *Thismethodisusedtocreatenewrecordsofthismodel
         *withprovideddata.Thisistheonlywaytocreatethem:
         *instantiationmustneverbeendonewithkeyword`new`outsideofthis
         *function,otherwisetherecordwillnotberegistered.
         *
         *@static
         *@param{Object|Object[]}[data]dataobjectwithinitialdata,includingrelations.
         * Ifdataisaniterable,multiplerecordswillbecreated.
         *@returns{mail.model|mail.model[]}newlycreatedrecord(s)
         */
        staticcreate(data){
            returnthis.env.modelManager.create(this,data);
        }

        /**
         *Gettherecordthathasprovidedcriteria,ifitexists.
         *
         *@static
         *@param{function}findFunc
         *@returns{mail.model|undefined}
         */
        staticfind(findFunc){
            returnthis.env.modelManager.find(this,findFunc);
        }

        /**
         *Getstheuniquerecordthatmatchesthegivenidentifyingdata,ifit
         *exists.
         *@see`_createRecordLocalId`forcriteriaofidentification.
         *
         *@static
         *@param{Object}data
         *@returns{mail.model|undefined}
         */
        staticfindFromIdentifyingData(data){
            returnthis.env.modelManager.findFromIdentifyingData(this,data);
        }

        /**
         *Thismethodreturnstherecordofthismodelthatmatchesprovided
         *localid.Usefultoconvertalocalidtoarecord.Notethateven
         *ifthere'sarecordinthesystemhavingprovidedlocalid,ifthe
         *resultingrecordisnotaninstanceofthismodel,thisgetter
         *assumestherecorddoesnotexist.
         *
         *@static
         *@param{string}localId
         *@param{Object}param1
         *@param{boolean}[param1.isCheckingInheritance]
         *@returns{mail.model|undefined}
         */
        staticget(localId,{isCheckingInheritance}={}){
            returnthis.env.modelManager.get(this,localId,{isCheckingInheritance});
        }

        /**
         *Thismethodcreatesarecordorupdatesone,depending
         *onprovideddata.
         *
         *@static
         *@param{Object|Object[]}data
         * Ifdataisaniterable,multiplerecordswillbecreated/updated.
         *@returns{mail.model|mail.model[]}createdorupdatedrecord(s).
         */
        staticinsert(data){
            returnthis.env.modelManager.insert(this,data);
        }

        /**
         *Performanasyncfunctionandwaituntilitisdone.Iftherecord
         *isdeleted,itraisesaRecordDeletedError.
         *
         *@param{function}funcanasyncfunction
         *@throws{RecordDeletedError}incasethecurrentrecordisnotalive
         *  attheendofasyncfunctioncall,whetherit'sresolvedor
         *  rejected.
         *@throws{any}forwardsanyerrorincasethecurrentrecordisstill
         *  aliveattheendofrejectedasyncfunctioncall.
         *@returns{any}resultofresolvedasyncfunction.
         */
        asyncasync(func){
            returnnewPromise((resolve,reject)=>{
                Promise.resolve(func()).then(result=>{
                    if(this.exists()){
                        resolve(result);
                    }else{
                        reject(newRecordDeletedError(this.localId));
                    }
                }).catch(error=>{
                    if(this.exists()){
                        reject(error);
                    }else{
                        reject(newRecordDeletedError(this.localId));
                    }
                });
            });
        }

        /**
         *Thismethoddeletesthisrecord.
         */
        delete(){
            this.env.modelManager.delete(this);
        }

        /**
         *Returnswhetherthecurrentrecordexists.
         *
         *@returns{boolean}
         */
        exists(){
            returnthis.env.modelManager.exists(this.constructor,this);
        }

        /**
         *Updatethisrecordwithprovideddata.
         *
         *@param{Object}[data={}]
         */
        update(data={}){
            this.env.modelManager.update(this,data);
        }

        //----------------------------------------------------------------------
        //Private
        //----------------------------------------------------------------------

        /**
         *Thismethodgeneratesalocalidforthisrecordthatis
         *beingcreatedatthemoment.
         *
         *Thisfunctionhelpscustomizingthelocalidtoeasemappingalocal
         *idtoitsrecordforthedeveloperthatreadsthelocalid.For
         *instance,thelocalidofathreadcachecouldcombinethethread
         *andstringifieddomaininitslocalid,whichismucheasierto
         *trackrelationsandrecordsinthesysteminsteadofarbitrary
         *numbertodifferenciatethem.
         *
         *@static
         *@private
         *@param{Object}data
         *@returns{string}
         */
        static_createRecordLocalId(data){
            return_.uniqueId(`${this.modelName}_`);
        }

        /**
         *Thisfunctioniscalledwhenthisrecordhasbeenexplicitlyupdated
         *with`.update()`orstaticmethod`.create()`,attheendofan
         *recordupdatecycle.Thisisabackward-compatiblebehaviourthat
         *isdeprecated:youshouldusecomputedfieldsinstead.
         *
         *@deprecated
         *@abstract
         *@private
         *@param{Object}previouscontainsdatathathavebeenstoredby
         *  `_updateBefore()`.Usefultomakeextraupdatedecisionsbasedon
         *  previousdata.
         */
        _updateAfter(previous){}

        /**
         *Thisfunctioniscalledjustatthebeginningofanexplicitupdate
         *onthisfunction,with`.update()`orstaticmethod`.create()`.This
         *isusefultorememberpreviousvaluesoffieldsin`_updateAfter`.
         *Thisisabackward-compatiblebehaviourthatisdeprecated:you
         *shouldusecomputedfieldsinstead.
         *
         *@deprecated
         *@abstract
         *@private
         *@param{Object}data
         *@returns{Object}
         */
        _updateBefore(){
            return{};
        }

    }

    /**
     *Modelsshoulddefinefieldsinstaticproporgetter`fields`.
     *Itcontainsanobjectwithnameoffieldaskeyandvalueareobjects
     *thatdefinethefield.Therearesomehelperstoeasethemakingofthese
     *objects,@see`mail/static/src/model/model_field.js`
     *
     *Note:fieldsofsuper-classareautomaticallyinherited,thereforea
     *sub-classshould(re-)definefieldswithoutcopyingancestors'fields.
     */
    Model.fields={};

    /**
     *Nameofthemodel.Importanttorefertoappropriatemodelclass
     *likeinrelationalfields.Nameofmodelclassesmustbeunique.
     */
    Model.modelName='mail.model';

    returnModel;
}

registerNewModel('mail.model',factory);

});
