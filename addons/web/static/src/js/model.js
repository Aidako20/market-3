flectra.define("web/static/src/js/model.js",function(require){
    "usestrict";

    const{groupBy,partitionBy}=require("web.utils");
    constRegistry=require("web.Registry");

    const{Component,core}=owl;
    const{EventBus,Observer}=core;
    constisNotNull=(val)=>val!==null&&val!==undefined;

    /**
     *FeatureextensionoftheclassModel.
     *@see{Model}
     */
    classModelExtension{
        /**
         *@param{Object}config
         *@param{Object}config.env
         */
        constructor(config){
            this.config=config;
            this.env=this.config.env;
            this.shouldLoad=true;
            this.state={};
        }

        //---------------------------------------------------------------------
        //Public
        //---------------------------------------------------------------------

        /**
         *Usedbytheparentmodeltoinitiatealoadaction.Theactual
         *loadingoftheextensionisdeterminedbythe"shouldLoad"property.
         *@param{Object}params
         */
        asynccallLoad(params){
            if(this.shouldLoad){
                this.shouldLoad=false;
                awaitthis.load(params);
            }
        }

        /**
         *@param{string}method
         *@param {...any}args
         */
        dispatch(method,...args){
            if(methodinthis){
                this[method](...args);
            }
        }

        /**
         *Exportsthecurrentstateoftheextension.
         *@returns{Object}
         */
        exportState(){
            returnthis.state;
        }

        /**
         *Meanttoreturntheresultoftheappropriategetterordonothing
         *ifnotconcernedbythegivenproperty.
         *@abstract
         *@param{string}property
         *@param {...any}args
         *@returns{null}
         */
        get(){
            returnnull;
        }

        /**
         *Importsthegivenstateafterparsingit.Ifnostateisgiventhe
         *extensionwillprepareanewstateandwillneedtobeloaded.
         *@param{Object}[state]
         */
        importState(state){
            this.shouldLoad=!state;
            if(this.shouldLoad){
                this.prepareState();
            }else{
                Object.assign(this.state,state);
            }
        }

        /**
         *Calledandawaitedoninitialmodelload.
         *@abstract
         *@param{Object}params
         *@returns{Promise}
         */
        asyncload(/*params*/){
            /*...*/
        }

        /**
         *Calledoninitializationifnoimportedstatefortheextensionis
         *found.
         *@abstract
         */
        prepareState(){
            /*...*/
        }
    }
    /**
     *Thelayerofanextensionindicateswithwhichotherextensionsthisone
     *willbeloaded.Thispropertymustbeoverriddenincasethemodel
     *dependsonotherextensionstobeloadedfirst.
     */
    ModelExtension.layer=0;

    /**
     *Model
     *
     *ThepurposeoftheclassModelandtheassociatedhookuseModel
     *istooffersomethingsimilartoanowlstorebutwithnoautomatic
     *notification(andrendering)ofcomponentswhenthe'state'usedinthe
     *modelwouldchange.Instead,oneshouldcallthe"__notifyComponents"
     *functionwheneveritisusefultoalertregisteredcomponent.
     *Nevertheless,whencallingamethodthroughthe'dispatch'method,a
     *notificationdoestakeplaceautomatically,andregisteredcomponents
     *(viauseModel)arerendered.
     *
     *Itishighlyexpectedthatthisclasswillchangeinanearfuture.We
     *don'thavethenecessaryhindsighttobesureitsactualformisgood.
     *
     *Thefollowingsnippetsshowatypicalusecaseofthemodelsystem:a
     *searchmodelwithacontrolpanelextensionfeature.
     *
     *-------------------------------------------------------------------------
     *MODELANDEXTENSIONSDEFINITION
     *-------------------------------------------------------------------------
     *
     *1.Definitionofthemainmodel
     *@seeModel
     *```
     * classActionModelextendsModel{
     *     //...
     * }
     *```
     *
     *2.Definitionofthemodelextension
     *@seeModelExtension
     *```
     * classControlPanelModelExtensionextendsActionModel.Extension{
     *     //...
     * }
     *```
     *
     *3.Registrationoftheextensionintothemainmodel
     *@seeRegistry()
     *```
     * ActionModel.registry.add("SearchPanel",ControlPanelModelExtension,10);
     *```
     *
     *-------------------------------------------------------------------------
     *ONVIEW/ACTIONINIT
     *-------------------------------------------------------------------------
     *
     *4.Creationofthecoremodelanditsextensions
     *@seeModel.prototype.constructor()
     *```
     * constextensions={
     *     SearchPanel:{
     *         //...
     *     }
     * }
     * constsearchModelConfig={
     *     //...
     * };
     * constactionModel=newActionModel(extensions,searchModelConfig);
     *```
     *
     *5.Loadingofallextensions'asynchronousdata
     *@seeModel.prototype.load()
     *```
     * awaitactionModel.load();
     *```
     *
     *6.Subscribingtothemodelchanges
     *@seeuseModel()
     *```
     * classControlPanelextendsComponent{
     *     constructor(){
     *         super(...arguments);
     *         //envmustcontaintheactionModel
     *         this.actionModel=useModel('actionModel');
     *     }
     * }
     *```
     *
     *-------------------------------------------------------------------------
     *MODELUSAGEONRUNTIME
     *-------------------------------------------------------------------------
     *
     *Case:dispatchanaction
     *@seeModel.prototype.dispatch()
     *```
     * actionModel.dispatch("updateProperty",value);
     *```
     *
     *Case:callagetter
     *@seeModel.prototype.get()
     *```
     * constresult=actionModel.get("property");
     *```
     *
     *@abstract
     *@extendsEventBus
     */
    classModelextendsEventBus{
        /**
         *Instantiatedextensionsaredeterminedbythe`extensions`argument:
         *-keysaretheextensionsnamesasaddedintheregistry
         *-valuesarethelocalconfigurationsgiventoeachextension
         *Theextensionsaregroupedbythesequencenumbertheywhere
         *registeredwithintheregistry.Extensionsbeingonthesamelevel
         *willbeloadedinparallel;thismeansthatallextensionsbelonging
         *tothesamegroupareawaitedbeforeloadingthenextgroup.
         *@param{Object<string,any>}[extensions={}]
         *@param{Object}[globalConfig={}]globalconfiguration:canbe
         *     accessedbyitselfandeachoftheaddedextensions.
         *@param{Object}[globalConfig.env]
         *@param{string}[globalConfig.importedState]
         */
        constructor(extensions={},globalConfig={}){
            super();

            this.config=globalConfig;
            this.env=this.config.env;

            this.dispatching=false;
            this.extensions=[];
            this.externalState={};
            this.mapping={};
            this.rev=1;

            const{name,registry}=this.constructor;
            if(!registry||!(registryinstanceofRegistry)){
                thrownewError(`Unimplementedregistryonmodel"${name}".`);
            }
            //Order,groupandsequenciallyinstantiateallextensions
            constregistryExtensions=Object.entries(registry.entries());
            constextensionNameLayers=registryExtensions.map(
                ([name,{layer}])=>({name,layer})
            );
            constgroupedNameLayers=groupBy(extensionNameLayers,"layer");
            for(constgroupNameLayersofObject.values(groupedNameLayers)){
                for(const{name}ofgroupNameLayers){
                    if(nameinextensions){
                        this.addExtension(name,extensions[name]);
                    }
                }
            }
            this.importState(this.config.importedState);
        }

        //---------------------------------------------------------------------
        //Public
        //---------------------------------------------------------------------

        /**
         *Methodusedinternallytoinstantiateallextensions.Canalsobe
         *calledexternallytoaddextensionsaftermodelinstantiation.
         *@param{string}extensionName
         *@param{Object}extensionConfig
         */
        addExtension(extensionName,extensionConfig){
            const{name,registry}=this.constructor;
            constExtension=registry.get(extensionName);
            if(!Extension){
                thrownewError(`Unknownmodelextension"${extensionName}"inmodel"${name}"`);
            }
            //Extensionconfig=this.config∪extension.config
            constget=this.__get.bind(this,Extension.name);
            consttrigger=this.trigger.bind(this);
            constconfig=Object.assign({get,trigger},this.config,extensionConfig);
            constextension=newExtension(config);
            if(!(Extension.layerinthis.extensions)){
                this.extensions[Extension.layer]=[];
            }
            this.extensions[Extension.layer].push(extension);
        }

        /**
         *Returnstheresultofthefirstrelatedmethodonanyinstantiated
         *extension.Thismethodmustbeoverriddenifmultipleextensions
         *returnavaluewithacommonmethod(anddispatchAlldoesnot
         *suffice).Afterthedispatchoftheaction,allmodelsarepartially
         *reloadedandcomponentsarenotifiedafterwards.
         *@param{string}method
         *@param{...any}args
         */
        dispatch(method,...args){
            constisInitialDispatch=!this.dispatching;
            this.dispatching=true;
            for(constextensionofthis.extensions.flat()){
                extension.dispatch(method,...args);
            }
            if(!isInitialDispatch){
                return;
            }
            this.dispatching=false;
            letrev=this.rev;
            //Calls'afterdispatch'hooks
            //Purpose:fetchupdateddatafromtheserver.Thisisconsidered
            //aloadingactionandisthusperformedbygroupsinsteadof
            //loadingallextensionsatonce.
            this._loadExtensions({isInitialLoad:false}).then(()=>{
                //Notifiessubscribedcomponents
                //Purpose:re-rendercomponentsboundby'useModel'
                if(rev===this.rev){
                    this._notifyComponents();
                }
            });
        }

        /**
         *Stringifiesandexportsanobjectholdingtheexportedstateofeach
         *activeextension.
         *@returns{string}
         */
        exportState(){
            constexported={};
            for(constextensionofthis.extensions.flat()){
                exported[extension.constructor.name]=extension.exportState();
            }
            constfullState=Object.assign({},this.externalState,exported);
            returnJSON.stringify(fullState);
        }

        /**
         *Returnstheresultofthefirstrelatedgetteronanyinstantiated
         *extension.Thismethodmustbeoverriddenifmultipleextensions
         *shareacommongetter(andgetAlldoesnotmakethejob).
         *@param{string}property
         *@param {...any}args
         *@returns{any}
         */
        get(property,...args){
            for(constextensionofthis.extensions.flat()){
                constresult=extension.get(property,...args);
                if(isNotNull(result)){
                    returnresult;
                }
            }
            returnnull;
        }

        /**
         *Parsesthegivenstringifiedstateobjectandimportseachstate
         *parttoitsrelatedextension.
         *@param{string}[stringifiedState="null"]
         */
        importState(stringifiedState="null"){
            conststate=JSON.parse(stringifiedState)||{};
            Object.assign(this.externalState,state);
            for(constextensionofthis.extensions.flat()){
                extension.importState(state[extension.constructor.name]);
            }
        }

        /**
         *Mustbecalledafterconstructionandstatepreparation/import.
         *Waitsforallasynchronousworkneededbythemodelextensionstobe
         *ready.
         */!\Thecurrentmodelextensionsdonotrequireasmartersystemat
         *themoment(thereforeusinglayersinsteadofdependencies).It
         *shouldbechangedifatsomepointanextensionneedsanother
         *specificextensiontobeloadedinsteadofawholebatch(withthe
         *currentsystemsomepromiseswillbewaitedneedlessly).
         *@returns{Promise}
         */
        asyncload(){
            awaitthis._loadExtensions({isInitialLoad:true});
        }

        //---------------------------------------------------------------------
        //Private
        //---------------------------------------------------------------------

        /**
         *Returnsthelistoftheresultsofallextensionsprovidingagetter
         *forthegivenpropertyreturninganon-nullvalue,excludingthe
         *extensionwhosenameisequalto"excluded".Thismethodisgivento
         *eachextensioninthe"config"objectboundtothemodelscopeand
         *havingtheextensionnameboundasthefirstargument.
         *@private
         *@param{string}excluded
         *@param{string}property
         *@param {...any}args
         *@returns{any[]}
         */
        __get(excluded,property,...args){
            constresults=[];
            for(constextensionofthis.extensions.flat()){
                if(extension.constructor.name!==excluded){
                    constresult=extension.get(property,...args);
                    if(isNotNull(result)){
                        results.push(result);
                    }
                }
            }
            returnresults;
        }

        /**
         *Privatehandlertoloopoverallextensionlayerssequenciallyand
         *waitforagivencallbacktobecompletedonallextensionsofa
         *samelayer.
         *@private
         *@param{Object}params
         *@param{boolean}params.isInitialLoadwhetherthiscallcomes
         *     fromtheinitialload.
         *@returns{Promise}
         */
        async_loadExtensions(params){
            for(letlayer=0;layer<this.extensions.length;layer++){
                awaitPromise.all(this.extensions[layer].map(
                    (extension)=>extension.callLoad(params)
                ));
            }
        }

        /**
         *@seeContext.__notifyComponents()inowl.jsforexplanation
         *@private
         */
        async_notifyComponents(){
            constrev=++this.rev;
            constsubscriptions=this.subscriptions.update||[];
            constgroups=partitionBy(subscriptions,(s)=>
                s.owner?s.owner.__owl__.depth:-1
            );
            for(letgroupofgroups){
                constproms=group.map((sub)=>
                    sub.callback.call(sub.owner,rev)
                );
                Component.scheduler.flush();
                awaitPromise.all(proms);
            }
        }
    }

    Model.Extension=ModelExtension;

    /**
     *Thisismoreorlessthehook'useContextWithCB'fromowlonlyslightly
     *simplified.
     *
     *@param{string}modelName
     *@returns{model}
     */
    functionuseModel(modelName){
        constcomponent=Component.current;
        constmodel=component.env[modelName];
        if(!(modelinstanceofModel)){
            thrownewError(`NoModelfoundwhenconnecting'${
                component.name
                }'`);
        }

        constmapping=model.mapping;
        const__owl__=component.__owl__;
        constcomponentId=__owl__.id;
        if(!__owl__.observer){
            __owl__.observer=newObserver();
            __owl__.observer.notifyCB=component.render.bind(component);
        }
        constcurrentCB=__owl__.observer.notifyCB;
        __owl__.observer.notifyCB=function(){
            if(model.rev>mapping[componentId]){
                return;
            }
            currentCB();
        };
        mapping[componentId]=0;
        constrenderFn=__owl__.renderFn;
        __owl__.renderFn=function(comp,params){
            mapping[componentId]=model.rev;
            returnrenderFn(comp,params);
        };

        model.on("update",component,async(modelRev)=>{
            if(mapping[componentId]<modelRev){
                mapping[componentId]=modelRev;
                awaitcomponent.render();
            }
        });

        const__destroy=component.__destroy;
        component.__destroy=(parent)=>{
            model.off("update",component);
            __destroy.call(component,parent);
        };

        returnmodel;
    }

    return{
        Model,
        useModel,
    };
});
